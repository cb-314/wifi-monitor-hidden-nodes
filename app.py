import subprocess
import time
from turtle import st

if __name__ == "__main__":
    adapter = "wlan0"

    # setup wifi adapter
    subprocess.call(["ifconfig", adapter, "down"])
    subprocess.call(["iwconfig", adapter, "mode", "monitor"])
    subprocess.call(["ifconfig", adapter, "up"])
    
    # start scanning
    #while True:
    for i in range(1):
        channel = 1
        scan_time = 5

        subprocess.call(["iwconfig", adapter, "channel", str(channel)])
        with subprocess.Popen((
            "tcpdump", 
            "-n", # don't convert addresses to names
            "-K", # don't verify TCP checksums
            "-t", # don't print timestamps
            "-l", # put the interface in "monitor mode"
            "-i", adapter), stdout=subprocess.PIPE) as p:
            start_time = time.time()
            try:
                for line in iter(p.stdout.readline, ""):
                    print(line)
            except:
                pass
            curr_time = time.time()
            if curr_time - start_time > scan_time:
                p.terminate()
