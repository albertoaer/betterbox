# BetterBox

Create distributed systems to run and share python code through a network

## Code Examples

Checkout [code examples](examples/loop)!

## What does Betterbox provide?
- Isolated and abstracted behave and code through the Box system
  - A Box is a class that works as a service
- RPC(Remote Procedure Call) system
  - A RemoteBox can call methods that might be run in a different host
- Client-Server structure with behaviour inheritance
  - A Remote Box inherit the remote functions from a Box or another RemoteBox
- Call serialization using the [dill](https://github.com/uqfoundation/dill) library
- Code injection using the SandBox
  - A SandBox has a Safe and an Unsafe version
- Parallel execution using the SpeadBox
- TCP Server and Clients (Transparent for the user)
- Threads for Server and Clients (Also Transparent for the user)
- Internal safe concurrent system

## What does Betterbox **not** provide?
- Any kind of concurrency or exclusion safety at Boxes implementation
  - Concurrency implementation rests on the user
  - RPC ensures transparency between remote calls but does not ensure synchronization between threads
  - Many clients calling one Server might be seen as many local threads calling the same method, and like so, concurrency safety is not ensured


## What might Betterbox provide in the future?
- SSL socket connection
- Persistent Boxes