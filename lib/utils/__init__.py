from .prettyprint import *

import subprocess
import re
from dotenv import load_dotenv
import os
load_dotenv()

class secrets:
    def_user = os.getenv("DEF_METER_USER")
    def_pass = os.getenv("DEF_METER_PASS")
    dev_mode = os.getenv('DEV', '0') == '1'

if secrets.dev_mode:
    print("          ===================          ", bg="#ffffff", fg="#ff00ff")
    print("          = DEV MODE ACTIVE =          ", bg="#ffffff", fg="#ff00ff")
    print("          ===================          ", bg="#ffffff", fg="#ff00ff")

# ['192.168.169.10', '192.168.169.11', '192.168.169.26', '192.168.169.33']
def get_devices():
    cmd_neightbors ="fping -a -g -p 1 -r 1 -t 50 192.168.169.10 192.168.169.40".split(' ')
    proc = subprocess.run(cmd_neightbors, capture_output=True, text=True)
    ips = proc.stdout.strip().splitlines()
    return ips

if __name__ == "__main__":
    print(get_devices())