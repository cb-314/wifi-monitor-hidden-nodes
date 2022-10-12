import subprocess
import time
import random
import csv

if __name__ == "__main__":
    # parameters
    adapter = "wlan0"
    n_loop = 10
    scan_time = 1
    output_name = "wmhn-result.csv"

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
    channels = {f:c for c, f in channels.items()}
    
    # main loop
    with open(output_name, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["loop", "time", "channel", "signal"])
        writer.writeheader()
        for idx_loop in range(n_loop):
            # set channel
            channel = random.choice([c for c in channels.values()])
            subprocess.call(["iwconfig", adapter, "channel", str(channel)])

            # add dummy row for the case there was no packet
            result = {
                "loop": idx_loop,
                "time": time.time(),
                "channel": channel,
                "signal": "" # this should work as empty
            }
            writer.writerow(result)

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
                        signal_max = max([int(float(s.replace("dBm", ""))) for s in signals])
                        result = {
                            "loop": idx_loop,
                            "time": time.time(),
                            "channel": channels[freq],
                            "signal": signal_max
                        }
                        writer.writerow(result)

                        # check if we have to stop
                        curr_time = time.time()
                        if curr_time - start_time > scan_time:
                            p.terminate()
                except:
                    pass