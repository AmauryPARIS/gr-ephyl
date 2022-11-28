from upper_class import upper 
import numpy, argparse

###############################
###     BS Upper 
### This is mearly an exemple of what an upper layer can look like
### Class function should be kept and used 'as is' 
### Decision making should be adapted

parser = argparse.ArgumentParser()
parser.add_argument('--ipAddr', help="IP address of the PHY layer", type= str, default="127.0.0.1")
parser.add_argument('--rxPort', help="Port used by the upper layer to receive the PHY layer feedbacks", type= str, default="5562")
parser.add_argument('--txPort', help="Port used by the upper layer to transmit instructions to the PHY layer", type= str, default="5561")
parser.add_argument('--bs',     help="Upper layer for BS (True) or sensor (False)", type= bool, default=True)
parser.add_argument('--list_sensors', help="List of used sensors ID", type= list, default=["A", "B"])
parser.add_argument('--slot_count', help="Number of slot used in the PHY layer", type= int, default=4)
parser.add_argument('--logged', help="Create log file", type= bool, default=False)
args=parser.parse_args()

up = upper( ipAddr = args.ipAddr, 
            rxPort = args.rxPort, txPort = args.txPort, 
            bs = args.bs, 
            list_sensors = args.list_sensors, slot_count = args.slot_count, 
            logged = args.logged
            )

while True:
    feedback_pmt = up.recv()
    feedback = up.extract(feedback_pmt)

    up.log(feedback["FRAME"], "Feedback received - frame : %s | ulcch : %s | rx : %s" % (feedback["FRAME"], feedback["ULCCH"], feedback["RX"]))
    print("Feedback received - frame : %s | ulcch : %s | rx : %s" % (feedback["FRAME"], feedback["ULCCH"], feedback["RX"]))

    list_dlcch = []
    frame = feedback["FRAME"] + 1

    for sensor in up.list_sensors:
        sn_id = sensor
        dlcch = str("dlcch_" + str(frame) + "_" + str(sn_id))
        list_dlcch.append([sn_id, dlcch])
    
    inst = up.create_BS_inst(list_dlcch, frame)
    up.send(inst)

    up.log(frame, "Instruction send - %s" % (inst))
    print("Instruction send - %s" % (inst))
