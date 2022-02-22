from sync_analysis import sync_analysis 
import matplotlib.pyplot as plt
import numpy as np

REMARK = "1 sensor"
sa = sync_analysis(local = True, 
                task = "LOCALX", 
                raw_sig = True)
sa.set_data_files()

sp = sa.get_file_samples()
metadata = sa.get_metadata(len(sp))

print("Samples length : %s" % (len(sp)))
for frame in metadata:
    print(frame)


###### Analyse de la puissance des échantillons par trames et par status  ######
## PRODUCE : task_XXXX_frames_YY_to_ZZ.png ##
print("## - Power over frame analysis")
sa.set_analysis_parameters(nb_subplot_per_img = 20, 
                            hor_nbr_subplt = 4, 
                            zoom = True, 
                            symb_len = 40)

RX_sig_start, BUSY_sig_start, RX_sig_start_nomod, BUSY_sig_start_nomod = sa.anaylise_frame(metadata, sp, REMARK, sig_start_analysis = True)

###### Analyse de l'échantillon de départ du signal sur toute la trame - Basé sur une fourchette de valeur de threshold  ######
## PRODUCE : task_XXXX_samp_start_by_power_tresh.png ##
print("## - Signal start over frame")
sa.analyse_sig_start_nomod(REMARK, RX_sig_start_nomod, BUSY_sig_start_nomod)

###### Analyse de l'échantillon de départ du signal au sein d'un symbol - Basé sur une fourchette de valeur de threshold  ######
## PRODUCE : task_XXXX_thresh_YY_to_ZZ.png ##
print("## - Signal start over symbol")
sa.analyse_sig_start(REMARK, RX_sig_start, BUSY_sig_start)

##### Analyse des supposés quatre premiers symboles - Basé sur UNE valeur de Thresholhd ######
## PRODUCE : task_XXXX_SYMB_start_for_frames_YY_to_ZZ.png ##
print("## - Presumed signal start")
sa.set_analysis_parameters(nb_subplot_per_img = 40, 
                            hor_nbr_subplt = 10, 
                            zoom = True, 
                            symb_len = 40,
                            sig_tresh = -33)

sa.analyse_symbol(metadata, sp, REMARK)

#sa.analyse_carrier(metadata, sp)


print("Processing done - Task %s - Local %s - RAW %s" % (sa.task, sa.local, sa.raw_sig))