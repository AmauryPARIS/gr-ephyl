from sync_analysis import sync_analysis 
import matplotlib.pyplot as plt
import numpy as np

REMARK = "1 sensor"
sa = sync_analysis(local = False, 
                task = "19024", 
                raw_sig = True)
sa.set_data_files()

sp = sa.get_file_samples()
metadata = sa.get_metadata(len(sp))

print("Samples length : %s" % (len(sp)))
for frame in metadata:
    print(frame)


# ###### Frame analysis ######
# print("Frame analysis")
# sa.set_analysis_parameters(nb_subplot_per_img = 20, 
#                             hor_nbr_subplt = 4, 
#                             zoom = True, 
#                             symb_len = 40)

# RX_sig_start, BUSY_sig_start, RX_sig_start_nomod, BUSY_sig_start_nomod = sa.anaylise_frame(metadata, sp, REMARK, sig_start_analysis = True)

# print("SIG START NOMOD")
# sa.analyse_sig_start_nomod(REMARK, RX_sig_start_nomod, BUSY_sig_start_nomod)

# ##### Sig Start analysis #####
# print("SIGSTART")
# sa.analyse_sig_start(REMARK, RX_sig_start, BUSY_sig_start)

##### Symbol analysis ######
print("Symbol analysis")
sa.set_analysis_parameters(nb_subplot_per_img = 40, 
                            hor_nbr_subplt = 10, 
                            zoom = True, 
                            symb_len = 40,
                            sig_tresh = -33)

sa.analyse_symbol(metadata, sp, REMARK)

#sa.analyse_carrier(metadata, sp)


print("Processing done - Task %s - Local %s - RAW %s" % (sa.task, sa.local, sa.raw_sig))