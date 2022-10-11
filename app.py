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

    # get channel list
    channels = subprocess.check_output(["iwlist", adapter, "channel"])
    channels = channels.decode("utf8").split("\n")
    channels = [c.strip() for c in channels]
    channels = [c.split(":") for c in channels if c.startswith("Channel")]
    channels = {int(c.replace("Channel", "").strip()): int(float(f.replace("GHz", "").strip())*1000) for c,f in channels}
    print(channels)
    
    # main loop
    #while True:
    for i in range(1):
        # parameters
        channel = 1
        scan_time = 3

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
                    freq = int(chunks[chunks.index("MHz")-1])
                    signals = [chunk for chunk in chunks if chunk.startswith("-") and chunk.endswith("dBm")]
                    signal_max = max([float(s.replace("dBm", "")) for s in signals])
                    print(freq, signal_max)

                    # check if we have to stop
                    curr_time = time.time()
                    if curr_time - start_time > scan_time:
                        p.terminate()
            except:
                pass