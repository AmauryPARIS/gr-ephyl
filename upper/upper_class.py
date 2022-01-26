import time, zmq, pmt, sys
from datetime import datetime


class upper:
    """
    Class made to manage and interact with a PHY layer entity within gnuradio
    Compatible with the modified gr_ephyl project 
    """

    def __init__(self, ipAddr = "127.0.0.1", rxPort = "5557", txPort = "5558", bs = True, list_sensors = ['A', 'B'], slot_count = 5, logged = False):
        # Variables
        self.ip = ipAddr
        self.rxPort = rxPort
        self.txPort = txPort
        self.bs = bs
        self.list_sensors = list_sensors
        self.slots = range(slot_count)
        self.logged = logged

        # Sockets
        context = zmq.Context()
        self.socket_RX = context.socket(zmq.SUB)
        self.socket_TX = context.socket(zmq.PUB)
        self.socket_RX.connect("tcp://%s:%s" % (self.ip, self.rxPort))
        self.socket_RX.setsockopt(zmq.SUBSCRIBE, b'')
        self.socket_TX.bind("tcp://%s:%s" % (self.ip, self.txPort))

        # Log filename
        if self.bs and self.log:
            self.filename_log = "LOG_BS_upper_"+time.strftime("%d%m%Y-%H%M%S")+".txt"
        elif not self.bs and self.log:
            self.filename_log = "LOG_SN_upper_"+time.strftime("%d%m%Y-%H%M%S")+".txt"

        self.log(0, "Init done")

    def log(self, frame, log):
        """ Create - if log is activated - a log in the specifed folder """
        if self.logged:
            now = datetime.now().time()
            with open(self.filename_log,"a+") as f_log:
                f_log.write("%s-%s-%s-%s\n" % ("UPPER", frame, now, log)) 
    
    def recv(self):
        """ Return any feedback received on the RX socket """
        return self.socket_RX.recv()

    def send(self, payload):
        """ Send new instruction on the TX socket """
        payload = pmt.serialize_str(payload)
        payload = pmt.to_pmt(payload)
        payload = pmt.serialize_str(payload)
        self.socket_TX.send(payload)

    def extract(self, feedbackPmt):
        """ 
        Extract all information for a feedback message received 
        Input :
            Received feedback at PMT format
        Return : 
            Dict with key depending on the entity status
                BS - [FRAME, ULCCH, RX]
                Sensor - [NODE, FRAME, DLCCH]
        """

        feedbackPmt = pmt.deserialize_str(feedbackPmt)

        if self.bs:

            # Current frame number
            frame_nbr = int(pmt.to_python(pmt.dict_ref(feedbackPmt, pmt.to_pmt("FRAME"), pmt.PMT_NIL))) 

            # List of [sensor ID, ULCCH message]
            ulcch = pmt.to_python(pmt.dict_ref(feedbackPmt, pmt.to_pmt("ULCCH"), pmt.PMT_NIL)) 

            # List of [slot_nbr, slot_status, slot_content]
            #   with slot_status in ["IDLE", "BUSY", "RX"]
            #   and slot_content - if status == "RX" - like [nodeId, payload]
            rx = pmt.to_python(pmt.dict_ref(feedbackPmt, pmt.to_pmt("RX"), pmt.PMT_NIL)) 

            # Log
            self.log(frame_nbr, "input - ULCCH : %s | RX : %s" % (ulcch, rx))

            return {"FRAME" : frame_nbr, "ULCCH" : ulcch, "RX" : rx }
        
        else:

            # Node whom the feedback comes from 
            sensor_id = pmt.to_python(pmt.dict_ref(feedbackPmt, pmt.to_pmt("NODE"), pmt.PMT_NIL)) 

            # Current frame number
            frame = int(pmt.to_python(pmt.dict_ref(feedbackPmt, pmt.to_pmt("FRAME"), pmt.PMT_NIL)))

            # Received DLCCH message
            dlcch = pmt.to_python(pmt.dict_ref(feedbackPmt, pmt.to_pmt("DLCCH"), pmt.PMT_NIL))

            # Log
            self.log(frame, "input - sensor : %s | DLCCH : %s" % (sensor_id, dlcch))

            return {"NODE" : sensor_id, "FRAME" : frame, "DLCCH" : dlcch}
        
    def create_BS_inst(self, listDlcch, frame):
        """ 
        Create the formatted dictionnary made to interact with the BS PHY layer 
            listDlcch - DLCCH messages to be send to node during next frame - [sn_id, dlcch]
            frame - Number of the next frame - int
        """
        msg = pmt.make_dict()
        msg = pmt.dict_add(msg, pmt.to_pmt("DLCCH"), pmt.to_pmt(listDlcch))
        msg = pmt.dict_add(msg, pmt.to_pmt("FRAME"), pmt.to_pmt(frame))
        self.log(frame, "Create new instruction - %s" % (msg))
        return msg

    def create_SN_inst(self, nodeId, frame, action, sequence, ulcch):
        """ 
        Create the formatted dictionnary to interact with a SN PHY layer 
            nodeId - sensor to whom the instruction are meant 
            frame - number of next frame - int
            action - Send a packet on real/simulated channel (True) or not (False) - bool
            sequence - Unicade character to send on the real/simulated channel if action == True
            ulcch - ULCCH message to send to the BS during next frame
        """
        msg = pmt.make_dict()
        msg = pmt.dict_add(msg, pmt.to_pmt("ID"), pmt.to_pmt(nodeId))
        msg = pmt.dict_add(msg, pmt.to_pmt("FRAME"), pmt.to_pmt(frame))
        msg = pmt.dict_add(msg, pmt.to_pmt("SEND"), pmt.to_pmt(action))
        msg = pmt.dict_add(msg, pmt.to_pmt("SEQUENCE"), pmt.to_pmt(sequence))
        msg = pmt.dict_add(msg, pmt.to_pmt("ULCCH"), pmt.to_pmt(ulcch))
        self.log(frame, "Create new instruction - %s" % (msg))
        return msg
