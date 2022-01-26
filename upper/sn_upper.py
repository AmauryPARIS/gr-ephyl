from upper_class import upper 
import numpy, argparse

###############################
###     SN Upper 
### This is mearly an exemple of what an upper layer can look like
### Class function should be kept and used 'as is' 
### Decision making should be adapted

parser = argparse.ArgumentParser()
parser.add_argument('--ipAddr', help="IP address of the PHY layer", type= str, default="127.0.0.1")
parser.add_argument('--rxPort', help="Port used by the upper layer to receive the PHY layer feedbacks", type= str, default="5560")
parser.add_argument('--txPort', help="Port used by the upper layer to transmit instructions to the PHY layer", type= str, default="5559")
parser.add_argument('--bs',     help="Upper layer for BS (True) or sensor (False)", type= bool, default=False)
parser.add_argument('--list_sensors', help="List of used sensors ID", type= list, default=["A", "B"])
parser.add_argument('--slot_count', help="Number of slot used in the PHY layer", type= int, default=5)
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

    up.log(feedback["NODE"], "SN - Feedback received - source sensor : %s | frame : %s | dlcch : %s" % (feedback["NODE"], feedback["FRAME"], feedback["DLCCH"]))
    print("SN - Feedback received - source sensor : %s | frame : %s | dlcch : %s" % (feedback["NODE"], feedback["FRAME"], feedback["DLCCH"]))

    action = "False"
    sequence = []
    frame = feedback["FRAME"] + 1
    ulcch = str("ulcch_" + str(frame) + "_" + str(feedback["NODE"]))
    
    for slot in up.slots:
        if numpy.random.uniform() < 0.5:
            action = "True"
            if numpy.random.uniform() < 0.5:
                sequence.append([slot, "Y"])
            else:
                sequence.append([slot, "X"])
        else:
            sequence.append([slot, False])

    inst = up.create_SN_inst(feedback["NODE"], frame, action, sequence, ulcch)
    up.send(inst)
    
    up.log(frame, "Instruction send - %s" % (inst))
    print("SN - Instruction send - %s" % (inst))
