import subprocess
import time
from turtle import st

if __name__ == "__main__":
    adapter = "wlan0"

    # setup wifi adapter
    subprocess.call(["ifconfig", adapter, "down"])
    subprocess.call(["iwconfig", adapter, "mode", "monitor"])
    subprocess.call(["ifconfig", adapter, "up"])

    # find your own mac addr
    output = subprocess.check_output(["ifconfig", "-a", adapter])
    my_addr = "-".join([x.lower() for x in output.split(" ")[output.split(" ").index("HWaddr")+1].split("-")[:6]])

    while True:
        channel = 1
        scan_time = 5

        subprocess.call(["iwconfig", adapter, "channel", str(channel)])
        with subprocess.Popen(("tcpdump", "-l", "-e", "-i", adapter), stdout=subprocess.PIPE) as p:
            start_time = time.time()
            try:
                for line in iter(p.stdout.readline, ""):
                    print(line)
            except:
                pass
            curr_time = time.time()
            if curr_time - start_time > scan_time:
                p.terminate()
