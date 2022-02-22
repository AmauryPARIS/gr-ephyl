import numpy as np
import re
import matplotlib
import matplotlib.pyplot as plt



class sync_analysis:

    def __init__(self, local = False, task = 19023, raw_sig = False):
        self.local = local
        self.task = task 
        self.raw_sig = raw_sig
    
    def set_data_files(self):
        # Path to data files 
        if self.local:
            path_to = "/root/"
        else:
            path_to = "/root/analysis/task_%s/node8/task_%s_container_0/root/cxlb_toolchain_build/gr-ephyl/examples/ml_mac/" % (self.task, self.task)
        
        # Raw signal files vs one carrier signal files
        if self.raw_sig:
            self.states_file = path_to + "STATE_BS.txt"
            self.samples_file = path_to + "BS_complex_2_32b"
        else:
            self.states_file = path_to + "STATE_Busy_Tresh.txt"
            self.samples_file = path_to + "BS_carrier_complex_2_32b"

        # RX status files [BUSY/IDLE/RX]
        self.rx_file = path_to + "RX_BS.txt"

    def get_file_samples(self):
        return np.fromfile(open(self.samples_file), dtype=np.complex64)

    def get_metadata(self, len_sp):
        states_f = open(self.states_file)
        rx_f = open(self.rx_file)
        states_lines = states_f.readlines()
        rx_lines = rx_f.readlines()
        
        frame = 0 
        keep_going = True
        start_frame = 0
        end_frame = 0

        metadata = []

        while keep_going: 
            push_samples = []
            slot_rx_status = []

            for i in range(0,len(states_lines)):
                intels = states_lines[i].split("-")
                index_correc = 0 if not self.raw_sig else 1
                if int(intels[1]) == frame + index_correc and intels[3] == "PROC":
                    end_frame = int(intels[4]) - 1
                elif int(intels[1]) == frame + index_correc -1 and intels[3] == "PUSCH":
                    try:
                        push_samples.append([int(intels[4]), int(states_lines[i+1].split("-")[4]) -1 ])
                    except:
                        push_samples.append([int(intels[4]), len_sp ])
            
            if end_frame < start_frame:
                end_frame = len_sp
                keep_going = False

            for i in range(0, len(rx_lines)):
                intels = rx_lines[i].split("-")
                if int(intels[0]) == frame:
                    slot_rx_status.append([intels[1], intels[2]]) # slot nbr, rx status
            
            metadata.append({"frame" : frame, "start" : start_frame, "end" : end_frame, "push" : push_samples, "rx" : slot_rx_status})

            start_frame = end_frame + 1
            frame += 1
        
        # Remove first and last frame because of missing samples
        return metadata[1:-1]

    def set_analysis_parameters(self, nb_subplot_per_img = 20, hor_nbr_subplt = 4, zoom = True, symb_len = 80, sig_tresh = -30):
        # Analysis 
        if self.raw_sig:
            self.downsampling_factor = 1
        else:
            self.downsampling_factor = 25

        self.number_of_subplot_per_image = nb_subplot_per_img
        self.hor_number_of_subplot = hor_nbr_subplt
        self.ver_number_of_subplot = int(self.number_of_subplot_per_image / self.hor_number_of_subplot)
        self.zoom = zoom
        self.symb_len = symb_len
        self.sig_tresh = sig_tresh
        if self.local:
            self.min_tresh_sig_start = -10
            self.max_tresh_sig_start = 20
        else:
            self.min_tresh_sig_start = -45
            self.max_tresh_sig_start = -10

    
    def set_subplot(self, note, anal_type):
        fig, axs = plt.subplots(self.hor_number_of_subplot, self.ver_number_of_subplot, figsize=(15,15))
        if self.raw_sig:
            data_type = "RAW_SIG"
        else:
            data_type = "SIG_CARRIER"
        
        if self.local:
            sig_type = "Simulation"
        else:
            sig_type = "CorteXlab"
        
        title = "Task %s - %s - Zoom on pusch slot : %s - %s - %s" % (self.task, data_type, self.zoom, note, sig_type)
        if anal_type == "frame":
            fig.suptitle('Power [dB] per frame - Colored samples match the RX slot for the BS\n %s' % (title))
        elif anal_type == "symbol":
            fig.suptitle('Power [dB] per samples - Each line match the fourth first symbol of a PUSCH and each plot match the %s samples of one symbol\n %s' % (self.symb_len, title))
        elif anal_type == "symbol_iq":
            fig.suptitle('IQ values per samples - Each line match the fourth first symbol of a PUSCH and each plot match the %s samples of one symbol \nI in blue - Q in red\n%s' % (self.symb_len, title))
        elif anal_type == "sig_start":
            fig.suptitle('Histogram for the number of samples between the symbol start and the signal start per power threshold value in [dB]\n Signal start detected by power threshold - Green is RX signal and red are BUSY signal\n %s' % (title))
        elif anal_type == "sig_start_nomod":
            fig.suptitle('First sample index to detect the thresh [dB] - Mean over each PUSH slot\n %s' % (title))
        fig.tight_layout(pad=3)

        return fig, axs

    def get_samples(self, frame, sp):
        if not self.zoom:
            samples = sp[frame["start"]:frame["end"]]
        else:
            push_start = frame["push"][0][0]
            push_end = frame["push"][-1][1]
            samples = sp[push_start:push_end]
        return samples

    def get_status(self, frame, i):
        return frame["rx"][i][1].replace("\n", "")
    
    def compute_samples_power_resamp(self, samples):
        samples_power = np.power(np.power(np.real(samples), 2) + np.power(np.imag(samples), 2), 0.5)
        samples_power = samples_power.reshape(-1, self.downsampling_factor)
        samples_power = np.mean(samples_power, 1)
        samples_power = 10*np.log10(samples_power)

        X = np.arange(0, len(samples), self.downsampling_factor)
        return X, samples_power

    def compute_samples_power(self, samples):
        samples_power = np.power(np.power(np.real(samples), 2) + np.power(np.imag(samples), 2), 0.5)
        samples_power = 10*np.log10(samples_power)
        X = np.arange(0, len(samples))
        return X, samples_power

    def get_push_index_resamp(self, frame, i):
        frame_start = frame["start"]
        push_samples_start = int((frame["push"][i][0] - frame_start) / self.downsampling_factor)
        push_samples_end = int((frame["push"][i][1] - frame_start) / self.downsampling_factor)
        print("frm start : %s, start %s, end %s, downsamp %s" % (frame_start, push_samples_start, push_samples_end, self.downsampling_factor))

        if not self.zoom:
            return push_samples_start, push_samples_end
        else:
            return 0, int((frame["push"][i][1] - frame["push"][i][0]) / self.downsampling_factor)

    def compute_push_power(self, push_sp):
        lin_power = np.power(np.power(np.real(push_sp), 2) + np.power(np.imag(push_sp), 2), 0.5)
        mean_lin_power = np.mean(lin_power)
        dB_push_power = 10*np.log10(mean_lin_power)
        print("PUSH power : %s" % dB_push_power)
        return dB_push_power

    def set_plot_vis(self, status):
        if status == "RX":
            fmt = '-g'
        elif status == "BUSY":
            fmt = '-r'
        else :
            fmt = '--y'
        return fmt

    def compute_sig_start(self, index_push_start, frame_status, no_resamp_sp):
        sig_start_analysis = "SIG_START_SAMP,%s" % frame_status
        sig_start_analysis_nomod = "SIG_START_SAMP_NO_MOD,%s" % frame_status
        list_sig_start = []
        list_sig_start_nomod = []
        for tresh in range(self.min_tresh_sig_start,self.max_tresh_sig_start):
            self.sig_tresh = tresh
            sig_start = self.get_samp_sig_start(self.compute_samples_power(no_resamp_sp)[1])
            sig_start_analysis_nomod += ",%s" % (sig_start)
            list_sig_start_nomod.append(sig_start)
            sig_start = (sig_start + index_push_start) % self.symb_len
            sig_start_analysis += ",%s" % sig_start
            list_sig_start.append(sig_start)

        print(sig_start_analysis)
        print(sig_start_analysis_nomod)
        return list_sig_start,list_sig_start_nomod


    def analyse_sig_start_nomod(self, remark, RX_sig_start, BUSY_sig_start):
        plt.clf()
        mean_RX_sig_start = np.mean(RX_sig_start, axis=0)
        mean_BUSY_sig_start = np.mean(BUSY_sig_start, axis=0)
        plt.figure(figsize=(10, 10))
        if len(mean_RX_sig_start) > 1:
            plt.plot(np.arange(self.min_tresh_sig_start,self.max_tresh_sig_start), mean_RX_sig_start, '-g', linewidth=0.75, label='RX')
        try:
            plt.plot(np.arange(self.min_tresh_sig_start,self.max_tresh_sig_start), mean_BUSY_sig_start, '-r', linewidth=0.75, label='BUSY')
        except:
            print("pas de données busy")
        
        plt.xlabel('Thresh value [dB]')
        plt.ylabel('Start sample')
        plt.title('Average signal start sample by power thresh')
        plt.legend() 
        plt.savefig("task_%s_samp_start_by_power_tresh.png" % (self.task))
        plt.clf()

    def analyse_sig_start(self, remark, RX_sig_start, BUSY_sig_start):

        fig, axs = self.set_subplot(note = remark, anal_type = "sig_start")

        ind_hor_subplt = 0
        ind_ver_subplt = 0
        ind_thresh = 0

        # X = Tresh values
        # i = index for tresh values
        # frame = index for frame values 
        print("Analyse sig start data")
        print("Tresh value [dB], min(busy), max(busy), mean(busy, min(RX), max(RX), mean(RX), min(BUSY) - max(RX), min(BUSY) - max(RX) > 0 ?")
        X_thresh = np.arange(self.min_tresh_sig_start,self.max_tresh_sig_start)
        for i in range(0, len(X_thresh)):
            if ind_thresh == 0:
                first_thresh_plt = X_thresh[i]

            axis = axs[ind_ver_subplt, ind_hor_subplt]

            BUSY_val = [BUSY_sig_start[frame][i] for frame in range(0,len(BUSY_sig_start))]
            RX_val = [RX_sig_start[frame][i] for frame in range(0,len(RX_sig_start))]

            X_delta_samp = np.arange(0,self.symb_len, 2)
            busy_hist = np.histogram(BUSY_val, X_delta_samp)
            rx_hist = np.histogram(RX_val, X_delta_samp)
            if not self.local:
                print("%s,%s,%s,%s,%s,%s,%s,%s,%s" % (X_thresh[i], min(BUSY_val), max(BUSY_val), np.mean(BUSY_val), min(RX_val), max(RX_val), np.mean(RX_val), min(BUSY_val) - max(RX_val), min(BUSY_val) - max(RX_val) >= 0))
            
            axis.plot(busy_hist[1][:-1], busy_hist[0], '-r', linewidth=0.75)
            axis.plot(rx_hist[1][:-1], rx_hist[0], '-g', linewidth=0.75)
            axis.set_title("Thresh = %s" % (X_thresh[i]))

            # Subplot index
            ind_thresh += 1
            if ind_hor_subplt == self.hor_number_of_subplot:
                ind_ver_subplt += 1
                ind_hor_subplt = 0
            else:
                ind_hor_subplt += 1

            if ind_thresh == self.number_of_subplot_per_image or i == len(X_thresh)-1:
                
                for ax in axs.flat:
                    ax.set(xlabel='Delta in samples', ylabel='Occurrence')

                plt.savefig("task_%s_thresh_%s_to_%s.png" % (self.task, first_thresh_plt, X_thresh[i]))
                plt.clf()

                fig, axs = self.set_subplot(note = remark, anal_type = "sig_start")

                ind_hor_subplt = 0
                ind_ver_subplt = 0
                ind_thresh = 0

    def anaylise_frame(self, metadata, sp, remark, sig_start_analysis):

        fig, axs = self.set_subplot(note = remark, anal_type = "frame")

        ind_hor_subplt = 0
        ind_ver_subplt = 0
        ind_frame = 0

        RX_sig_start = []
        BUSY_sig_start = []
        RX_sig_start_nomod = []
        BUSY_sig_start_nomod = []

        for frame in metadata:
            print("\nFrame nbr %s" % (frame["frame"]))
            plot_name = "Frame_%s" % frame["frame"]
            axis = axs[ind_ver_subplt, ind_hor_subplt]

            samples = self.get_samples(frame, sp)  
            while len(samples) % self.downsampling_factor != 0:
                samples = samples[:-1]  

            X, samples_power = self.compute_samples_power_resamp(samples)

            print("mean samples frame %s" % np.mean(samples_power))

            axis.plot(X, samples_power, '-k', linewidth=0.75)
            axis.set_ylim([np.nanmin(samples_power[samples_power != -np.inf])-2.5, np.nanmax(samples_power[samples_power != -np.inf])+2.5])

            for i in range(0,len(frame["rx"])):
                status = self.get_status(frame, i)
                
                push_samples_start, push_samples_end = self.get_push_index_resamp(frame, i)
                push_power = self.compute_push_power(sp[frame["push"][i][0]:frame["push"][i][1]])
                fmt = self.set_plot_vis(status)
                print("fmt %s" % fmt)
                print("PUSH %s - %s" % (frame["push"][i][0],frame["push"][i][1]))
                print("PUSH index resamp %s - %s" % (push_samples_start, push_samples_end))
                print("len samp resamp %s" % len(X))
                
                if sig_start_analysis:
                    if status == "RX":
                        lst_sig_start, lst_sig_start_nomod = self.compute_sig_start(frame["push"][i][0],status,sp[frame["push"][i][0]:frame["push"][i][1]])
                        RX_sig_start.append(lst_sig_start)
                        RX_sig_start_nomod.append(lst_sig_start_nomod)
                    elif status == "BUSY":
                        lst_sig_start, lst_sig_start_nomod = self.compute_sig_start(frame["push"][i][0],status,sp[frame["push"][i][0]:frame["push"][i][1]])
                        BUSY_sig_start.append(lst_sig_start)
                        BUSY_sig_start_nomod.append(lst_sig_start_nomod)            
                
                plot_name += "_%s_%s" % (status, np.around(push_power, decimals=2))
                axis.plot(X[push_samples_start:push_samples_end], samples_power[push_samples_start:push_samples_end] ,fmt, linewidth=2)
                print("Slot %s - %s" %(frame["rx"][i][0], status))
 
            axis.set_title("%s" % plot_name)

            # Subplot index
            ind_frame += 1
            if ind_hor_subplt == self.hor_number_of_subplot:
                ind_ver_subplt += 1
                ind_hor_subplt = 0
            else:
                ind_hor_subplt += 1

            if ind_frame == self.number_of_subplot_per_image or frame["frame"] == len(metadata):
                
                for ax in axs.flat:
                    ax.set(xlabel='Samples', ylabel='Power [dB]')

                plt.savefig("task_%s_frames_%s_to_%s.png" % (self.task, frame["frame"] - ind_frame, frame["frame"]))
                plt.clf()

                fig, axs = self.set_subplot(note = remark, anal_type = "frame")

                ind_hor_subplt = 0
                ind_ver_subplt = 0
                ind_frame = 0

        return RX_sig_start, BUSY_sig_start, RX_sig_start_nomod, BUSY_sig_start_nomod

    def get_frame_meta(self, metadata, frame_index):
        for frame_meta in metadata:
            if frame_index == frame_meta["frame"]:
                return frame_meta
        print("Meta not found")
        return None

    def get_symb_sig_start(self, samples):
        for i in range(0, len(samples), self.symb_len):
            if samples[i] > self.sig_tresh:
                return i - self.symb_len
        print("You got NO power on this frame")
        return 0

    def get_samp_sig_start(self, samples):

        for i in range(0, len(samples)):
            if samples[i] > self.sig_tresh:
                return i
        print("You got NO power on this frame")
        return 0

    def analyse_symbol(self, meta, sp, remark, sig_type):
        if sig_type == "dB":
            fig, axs = self.set_subplot(note = remark, anal_type = "symbol")
        elif sig_type == "IQ":
            fig, axs = self.set_subplot(note = remark, anal_type = "symbol_iq")
        else:
            print("Error - unknown type of analysis")
            return 0

        ind_hor_subplt = 0
        ind_ver_subplt = 0
        ind_symb = 0

        self.zoom = True
        self.downsampling_factor = 1

        if self.local:
            self.sig_tresh = -5

        for frame_meta in meta:
            
            print("Frame %s " % (frame_meta["frame"]))
            samples = self.get_samples(frame_meta, sp)
            X, samples_power = self.compute_samples_power(samples) #no resamp

            frame_rx_status = ""
            for rx_status in frame_meta["rx"]:
                frame_rx_status += "_%s" % rx_status[1].replace("\n", "")
            
            if frame_meta["rx"][0][1].replace("\n","") in ["RX", "BUSY"]:

                sig_start = self.get_symb_sig_start(samples_power) 
                print("index samp push start : %s" % (frame_meta["push"][0][0]))
                print("value %s, %s, %s" % (sp[frame_meta["push"][0][0]-1], sp[frame_meta["push"][0][0]], sp[frame_meta["push"][0][0]+1]))
                print("mod index samp push start : %s" % (frame_meta["push"][0][0] % self.symb_len))
                sig_start_sample = (frame_meta["push"][0][0] + self.get_samp_sig_start(samples_power)) % self.symb_len

                for i in range(0,4):
                    print("ind sb plt %s - %s" % (ind_hor_subplt, ind_ver_subplt))
                    axis = axs[ind_ver_subplt, ind_hor_subplt]
                    index_start = sig_start + (i * self.symb_len)
                    index_stop = sig_start + ((i+1) * self.symb_len) -1

                    if sig_type == "dB":
                        fmt = self.set_plot_vis(frame_meta["rx"][0][1].replace("\n",""))
                        axis.plot(X[index_start:index_stop], samples_power[index_start:index_stop] ,fmt, linewidth=1)
                        if not self.local:
                            axis.set_ylim([-22, -20])

                    elif sig_type == "IQ":
                        axis.plot(X[index_start:index_stop], np.real(samples[index_start:index_stop]) ,"b", linewidth=1)
                        axis.plot(X[index_start:index_stop], np.imag(samples[index_start:index_stop]) ,"r", linewidth=1)

                    axis.set_title("frme_%s_sp_%s_to_%s" % (frame_meta["frame"], index_start, index_stop))

                    # Subplot index

                    if ind_hor_subplt == 0 and ind_ver_subplt == 0:
                        start_frame_plt = frame_meta["frame"]

                    ind_symb += 1
                    if ind_hor_subplt == self.ver_number_of_subplot-1:
                        ind_ver_subplt += 1
                        ind_hor_subplt = 0
                    else:
                        ind_hor_subplt += 1

                    

                    if ind_symb == self.number_of_subplot_per_image :
                        
                        for ax in axs.flat:
                            ax.set(xlabel='Samples', ylabel='Power [dB]')

                        plt.savefig("task_%s_SYMB_start_for_frames_%s_to_%s_sig_%s.png" % (self.task, start_frame_plt, frame_meta["frame"], sig_type))
                        plt.clf()

                        if sig_type == "dB":
                            fig, axs = self.set_subplot(note = remark, anal_type = "symbol")
                        elif sig_type == "IQ":
                            fig, axs = self.set_subplot(note = remark, anal_type = "symbol_iq")

                        ind_hor_subplt = 0
                        ind_ver_subplt = 0
                        ind_symb = 0
        
            for i in range(0,len(frame_meta["rx"])):
                print("Slot %s - Power = %s [dB] - Status %s" % (i, self.compute_push_power(sp[frame_meta["push"][i][0]:frame_meta["push"][i][1]]), frame_meta["rx"][i][1]))


    def analyse_carrier(self, metadata, sp):
        for frame in metadata:
            push_index = frame["push"][0][0]
            push_index_stop = frame["push"][0][1]

            print("%s,%s,%s,%s" % (frame["frame"], sp[push_index-1], sp[push_index], sp[push_index+1]))

