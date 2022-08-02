# BetterBox

Create distributed systems to run and share python code through a network

# ADVISE: Everything in this *readme* is `conceptual` !
# Objetives

- Provide a generic distributed systems interface for sharing python code and services through a network (**The Boxes**)
- Specialize boxes in different fields such as hard computational boxes or boxes dedicated to microservices
- Allow serialization of any python object through the network and its replication
- Create a well-defined network protocol for boxes communication

# Standard Boxes

- Box: Default box that exports functions to the ones that inherit it
- SandBox: Like a box but allowing code injection

- RemoteBox: Represents a box that is not in the current machine
- GroupBox: RemoteBox specialization that matches many boxes
- SpreadBox: GroupBox specialization for computational requirements

# Always execute

If any Remote like box does not find at least one box instance in the network won't even start

RemoteBox always keep the first box that responses
GroupBox and SpreadBox will keep them all

GroupBox and SpreadBox will target all the boxes when a invokation occurs, also SpreadBox can spread over the targets avoiding too much overload

Invokation result is always a Promise, with methods:
- any: gets only the first response
- all: gets an array of responses
- compute: uses a custom function in order to get a single value

# Syntax

## Server

```python
from betterbox import Box, serve_box

@serve_box(8090)
class ABox(Box):
    def name(self) -> str: return 'MyBox'
```

## Client

```python
from betterbox import RemoteBox, use_box

@use_box(8090)
class OtherBox(RemoteBox):
    def __init__(self):
        print(f'I m {self.name().any()}')
```

### A client can also serve itself

```python
from betterbox import RemoteBox, serve_box, use_box

@serve_box(9090)
@use_box(8090)
class OtherBox(RemoteBox):
    def __init__(self):
        print(f'I m {self.name().any()}')
```

### Persistents boxes

Boxes can be loaded before being served and saved after being stopped

```python
from betterbox import Box, serve_box, persist

@serve_box(8090)
@persist('abox')
class ABox(Box):
    data: str
```