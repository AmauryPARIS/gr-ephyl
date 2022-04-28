from upper_class import upper 
import numpy

###############################
###     Upper 
### This is mearly an exemple of what an upper layer can look like
### Class function should be kept and used 'as is' 
### Decision making should be adapted

up = upper( ipAddr = "127.0.0.1", 
            rxPort = "5557", txPort = "5558", 
            bs = False, 
            list_sensors = ['A', 'B'], slot_count = 5, 
            logged = True
            )

while True:
    feedback_pmt = up.recv()
    feedback = up.extract(feedback_pmt)

    print("SN - Feedback received - source sensor : %s | frame : %s | dlcch : %s" % (feedback["NODE"], feedback["FRAME"], feedback["DLCCH"]))

    action = "True"
    sequence = []
    frame = frame + 1
    
    for slot in up.slots:
        if numpy.random.uniform() < 0.9:
            if numpy.random.uniform() < 0.5:
                sequence.append([slot, "Y"])
            else:
                sequence.append([slot, "X"])
        else:
            sequence.append([slot, False])
    
    if len(sequence) == 0:
        action = "False"

    inst = up.create_BS_inst(list_dlcch, feedback["FRAME"] + 1)
    up.send(inst)
    print("SN - Instruction send - %s" % (inst))



### Problème : modification non prise en compte à l'execution 
# conflit entre le log attribut à l'init 
# et la fonction self.log 
