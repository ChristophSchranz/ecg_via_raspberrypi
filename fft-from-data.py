import time
import json
import os
import pandas as pd
import numpy as np
import scipy
import scipy.fftpack
import datetime as datetime
import matplotlib.pyplot as plt
import matplotlib


def fft():
    df = pd.read_csv("data/ekg_data.csv", names=["time", "voltage"])
    tsmin = df["time"].min()
    df.index = df["time"]/60  # 60 Hz is one beat per second
    df = df["voltage"]
    print(df.shape, df.head())

    create_fft_plot(df, tsmin)


def create_fft_plot(df, tsmin):
    #font = {"family": "normal", "weight": "bold", "size": 22}
    #matplotlib.rc("font", **font)
    matplotlib.rcParams.update({"font.size": 15})
    #matplotlib.rc("axes", edgecolor="white")
    
    # Filtering df to the samples we are interested in
    #df[(df < df.quantile(0.025)) | (df.quantile(0.975) < df)] = np.nan
    #fltdf = df.interpolate(method="index")
    fltdf = df - df.median()
    
    # Initialising the Plot
    fig = plt.figure(figsize=(20,5.5))
    #fig.patch.set_facecolor("black")
      
    delta_t = (fltdf.index[-1] - fltdf.index[0]) # length of the time period in seconds
    x = np.linspace(0.0, delta_t, len(fltdf))
      
    ax1 = plt.subplot(1,2,1)     
    ax1.plot(x, fltdf, linewidth=2.0)

    ax1.tick_params(axis="x")
    ax1.tick_params(axis="y")
    date = datetime.datetime.fromtimestamp(tsmin).strftime('%Y-%m-%d')
    daytime = datetime.datetime.fromtimestamp(tsmin).strftime('%H-%M-%S')
    ax1.set_title("Heartbeat time-series from {}\n at {}".format(date, daytime))
    ax1.set_xlabel("Time in s")
    ax1.set_ylabel("Measured Voltage in V",)

    N = fltdf.shape[0]
    yf = scipy.fftpack.fft(fltdf) # the actual fourier transformation

    ax2 = plt.subplot(1,2,2)
    
    freq = scipy.fftpack.fftfreq(N, delta_t/N)
    FFT = np.abs(yf)
    ax2.plot(freq, 20*np.log10(FFT))#, ".")
    ax2.set_ylim(0, 50)
    ax2.set_xlim(25, 200)
    ax2.tick_params(axis="x")
    ax2.tick_params(axis="y")
    ax2.set_title("Heartbeat Frequency Spektrum")
    ax2.set_xlabel("Frequency in beat per minute")
    ax2.set_ylabel("Amplitude in dB")
    if not os.path.exists("fft/{}".format(date)):
        os.makedirs("fft/{}".format(date))

    filename = "fft/{}/{}-fft-{}.png".format(date, daytime, int(N/1000))
    plt.savefig(filename, bbox_inches="tight", transparent=False)
    plt.show()


# The code will be started from this point on.
if __name__ == "__main__":
    print("Reading EKG measurement and do Fast Fourier-Transformation")
    # The function measure_voltage will be executed (called) with the argument
    # "channel" which was defined on at the top of the code.
    fft()
