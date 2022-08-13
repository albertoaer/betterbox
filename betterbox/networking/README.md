# The Betterbox Networking Protocol

The normal stream of packets is:
- Client Request (with a client action)
- Server Response (with a server action)

## Message Format

status_byte = length_nible + action_nibble

A nibble max value is 15 in decimal

(length_nibble)(action_nibble)[ message...length-1 ]

The length nibble sets the buffer size, a size enough to hold the input data:
2 ** length_nibble

The action nibble determines a low level server-client action, except the app action for sending to the box the message payload (might require login)

## Actions of Client and Server

- app (code: 0)
- notify (code: 1)

## Clients actions

The standard client actions are:
- ping (code: 2)
- login (code: 3)

## Server actions

The standard server actions are:
- found (code: 4) (responds: ping)
- grant (code: 5) (responds: login)
- denie (code: 6) (responds: login)