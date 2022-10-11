import subprocess
import time
from turtle import st

if __name__ == "__main__":
    # parameters
    adapter = "wlan0"

    # setup wifi adapter
    subprocess.call(["ifconfig", adapter, "down"])
    subprocess.call(["iwconfig", adapter, "mode", "monitor"])
    subprocess.call(["ifconfig", adapter, "up"])
    
    # main loop
    #while True:
    for i in range(1):
        # parameters
        channel = 1
        scan_time = 1

        # set channel
        subprocess.call(["iwconfig", adapter, "channel", str(channel)])

        # start scanning
        start_time = time.time()
        with subprocess.Popen(
            (
                "tcpdump", 
                "-n", # don't convert addresses to names
                "-K", # don't verify TCP checksums
                "-t", # don't print timestamps
                "-l", # put the interface in "monitor mode"
                "-y", "IEEE802_11_RADIO", # activate radiotap headers explicitly
                "-i", adapter
            ), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as p:
            try:
                for line in iter(p.stdout.readline, ""):
                    # parse line
                    line = line.decode("utf8")
                    chunks = line.split(" ")
                    signals = [chunk for chunk in chunks if chunk.startswith("-") and chunk.endswith("dBm")]
                    signal_max = max([float(s.replace("dBm", "")) for s in signals])
                    print(signals, signal_max)

                    # check if we have to stop
                    curr_time = time.time()
                    print(curr_time - start_time, scan_time)
                    if curr_time - start_time > scan_time:
                        p.terminate()
            except:
                pass