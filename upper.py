import time
import zmq
import pmt

context = zmq.Context()
socket_RX = context.socket(zmq.SUB)
socket_TX = context.socket(zmq.PUB)
socket_RX.connect("tcp://127.0.0.1:5557")
socket_RX.setsockopt(zmq.SUBSCRIBE, b'')
socket_TX.bind("tcp://127.0.0.1:5558")

while True:
    #  Wait for next request from client
    message = socket_RX.recv()
    print("Received request: %s" % pmt.to_python(pmt.deserialize_str(message)))


    #  Do some 'work'
    #time.sleep(0.5)

    #  Send reply back to client
    socket_TX.send(pmt.serialize_str(pmt.to_pmt('True')))


