import streamlit as st
from plot_cont import DynamicPlot
from capture_frames import CaptureFrames
from process_mask import ProcessMasks
from utils import *
import time
import multiprocessing as mp

class RunPOS():
    def __init__(self, sz=270, fs=28, bs=30, plot=True):
        self.batch_size = bs 
        self.frame_rate = fs
        self.signal_size = sz
        self.plot = plot

    def run(self, source, sz, fs, bs):
        time1 = time.time()

        mask_process_pipe, chil_process_pipe = mp.Pipe() # multiprocessing 

        self.plot_pipe = None 
        if self.plot:
            self.plot_pipe, plotter_pipe = mp.Pipe() # multiprocessing
            self.plotter = DynamicPlot(self.signal_size, self.batch_size)
            self.plot_process = mp.Process(target=self.plotter, args=(plotter_pipe,), daemon=True) # multiprocessing
            self.plot_process.start()
        
        process_mask = ProcessMasks(self.signal_size, self.frame_rate, self.batch_size)

        mask_processer = mp.Process(target=process_mask, args=(chil_process_pipe, self.plot_pipe, source, ), daemon=True)  # multiprocessing

        mask_processer.start()
        
        capture = CaptureFrames(self.batch_size, source, show_mask=True) 

        capture(mask_process_pipe, source)

        mask_processer.join()
        if self.plot:
            self.plot_process.join()
        time2 = time.time()
        print(f'time {time2-time1}')

def main():
    st.title("Health Vital Analysis")

    sz = st.slider("Signal Size", min_value=100, max_value=500, value=270)
    fs = st.slider("Frame Rate", min_value=1, max_value=60, value=28)
    bs = st.slider("Batch Size", min_value=10, max_value=100, value=30)

    plot = st.checkbox("Show Plot", value=True)

    runPOS = RunPOS()

    if st.button("Run Analysis"):
        st.write("Running analysis...")
        runPOS.run(source, sz, fs, bs)

if __name__ == "__main__":
    main()
