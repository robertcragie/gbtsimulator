# GBT Simulator

This is a very basic Python 3 GBT simulator that attempts to implement the GBT procedures identified in the DLMS Green Book (DLMS UA 1000-2 Ed.11 V1.0) to enable understanding.

It uses a client thread and a server thread to simulate two parties communicating using GBT. The parameters at the top of [GBT.py](GBT.py) control block sizing etc.:

## Configuration

The following values are hard-coded in [GBT.py](GBT.py) and can be modified. Ideally all of these would be configurable through the app.

```python
# GBT constants
GBT_MAX_PAYLOAD = 10 # Keep it small for simulator

# Streaming and windowing parameters
# Current set to those imposed by GBCS
GBT_CLT_BTS = 1  # Always confirmed
GBT_CLT_BTW = 63 # The number of blocks a client can receive in one window
GBT_SVR_BTS = 1  # Always confirmed
GBT_SVR_BTW = 6  # The number of blocks a server can receive in one window
```

## Message dropping

The app allows simple simulated message dropping based on the block number. The two lists at the top of [GBT.py](GBT.py) are used:

```python
# Block number (BN) of message to drop (1 = first, 2 = second etc.)
aCltDropBlocks = []
aSvrDropBlocks = [1,3]
```

If the list is empty, no messages are dropped. Note that once a block has been dropped, any subsequent retry will not be dropped.

## Timeouts

Server and client transmit and receive timeouts can be set in [GBT.py](GBT.py):

```python
# Timeouts in seconds for server and client.
tTxTimeouts = (5.0, 10.0) # Server, client. Timeout waiting for ack.
tRxTimeouts = (5.0, 10.0) # Server, client. Timeout waiting for next rx.
```

## App types

There is both a wxPython app and a CLI app.

The wxPython app allows easier execution and parameter modification through a GUI. Its operation is basic at the moment but provides a template for further modification. It requires [wxPython](https://www.wxpython.org/) to be installed.

To run the wxPython version, execute:

    python GBTSimulator.py

The CLI app is essentially the same but uses the saved payload and invokes as GBT client to keep it simple. Its operation is basic at the moment but provides a template for further modification.

To run the CLI version, execute:

    python gbtsimcli.py

An example message sequence chart that can be used in [sequencediagram.org](https://sequencediagram.org/) is produced in [msc.txt](msc.txt).