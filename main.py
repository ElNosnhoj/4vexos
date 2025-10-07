import threading
from typing import Dict
from lib.escposprinter import FilePrinter
from lib.ssh.meter import SSHMeter
from lib.utils import get_devices, secrets
import time
import os
from lib.utils import print
from lib.config import ModuleSettings
import json

# ASSUME NO OTHER USB DEVICES PLUGGEDIN
printer_path = "/dev/usb/lp0"
printer = FilePrinter(printer_path)


class zebra:
    def simple(hostname,modules):
        top = f"meter: {hostname}"
        table_header = "module".ljust(14)+" | "
        table_header+= "ver".rjust(4)+" | "
        table_header+= "mod".rjust(4)+" | "
        table_header+= "id".rjust(9)

        table_rows = []
        for k, v in modules.items(): 
            # p.line(f"{k}: v{v.get('fw')} | mf{v.get('mod_func')} | id{v.get('full_id')}")
            line = k.ljust(14)+" | "
            line+= str(v.get('fw')).rjust(4) + " | "
            line+= str(v.get('mod_func')).rjust(4) + " | "
            line+= str(v.get('full_id')).rjust(9)
            table_rows.append(line)
        
        if secrets.dev_mode:
            print(top)
            print(json.dumps(table_rows, indent=4))
            print("pretend print success", fg="#ffffff", bg="#00ff00")

        else:
            printer.line(top)
            printer.line(table_header)
            for row in table_rows: printer.line(row)
            printer.cut()
        

    def organized(hostname,modules):
        equals = "=" * 40
        top=[equals]
        top.append(f"meter: {hostname}")
        bot=[equals]

        table_header = "module".ljust(14)+" | "
        table_header+= "ver".rjust(4)+" | "
        table_header+= "mod".rjust(4)+" | "
        table_header+= "id".rjust(9)
        top.append(table_header)

        # good = module matches config
        # bad = module mismatches config
        # missing = config has something meter does not
        # extra = meter has something config does not
        good, bad, extra, missing  = {}, {}, {}, {}
        
        for k, v in modules.items():
            to_check = {"version": v["fw"], "mod": v["mod_func"]}
            stored = ModuleSettings[k]
            if not stored: extra[k] = v
            elif stored==to_check: good[k] = v
            else: bad[k] =v
        for k in ModuleSettings.get_keys():
            if k not in modules:
                missing[k] = ModuleSettings[k]

        rows = []
        def __rows(d:dict):
            for k,v in d.items():
                line = k.ljust(14)+" | "
                line+= str(v.get('fw')).rjust(4) + " | "
                line+= str(v.get('mod_func')).rjust(4) + " | "
                line+= str(v.get('full_id')).rjust(9)
                rows.append(line)

        
        if good:
            rows.append('========================================')
            rows.append('=========         pass          ========')
            rows.append('========================================')
            __rows(good)
        if bad:
            rows.append('========================================')
            rows.append('=========         fail          ========')
            rows.append('========================================')
            __rows(bad)
        if missing:
            rows.append('========================================')
            rows.append('=======         missing          =======')
            rows.append('========================================')
            __rows(missing)
        if extra:
            rows.append('========================================')
            rows.append('========         extra          ========')
            rows.append('========================================')
            __rows(extra)

        if secrets.dev_mode:
            # print(json.dumps(top, indent=4))
            for l in top: print(l)
            for l in rows: print(l)
            for l in bot: print(l)
            

        else:
            for l in top: printer.line(l)
            for l in rows: printer.line(l)
            for l in bot: printer.line(l)
            printer.cut()
    
    def organizedv2(hostname,modules):
        equals = "=" * 42
        top=[equals]
        top.append(f"meter: {hostname}")
        bot = [equals]

        table_header = " |"
        table_header+= "module".ljust(14)+" | "
        table_header+= "ver".rjust(4)+" | "
        table_header+= "mod".rjust(4)+" | "
        table_header+= "id".rjust(9)
        top.append(table_header)

        # good = module matches config
        # bad = module mismatches config
        # missing = config has something meter does not
        # extra = meter has something config does not
        good, bad, extra, missing  = {}, {}, {}, {}
        
        for k, v in modules.items():
            to_check = {"version": v["fw"], "mod": v["mod_func"]}
            stored = ModuleSettings[k]
            if not stored: extra[k] = v
            elif stored==to_check: good[k] = v
            else: bad[k] =v
        for k in ModuleSettings.get_keys():
            if k not in modules:
                missing[k] = ModuleSettings[k]

        rows = []
        def __rows(d:dict, pre):
            for k,v in d.items():
                line=f"{pre}|"
                
                line+= k.ljust(14)+" | "
                line+= str(v.get('fw')).rjust(4) + " | "
                line+= str(v.get('mod_func')).rjust(4) + " | "
                line+= str(v.get('full_id')).rjust(9)
                rows.append(line)

        
        if good: __rows(good, 'Y')
        if bad: __rows(bad, 'N')
        if missing: __rows(missing, '-')
        if extra: __rows(extra, '+')
            
        combined = top+rows+bot
        if secrets.dev_mode:
            # print(json.dumps(top, indent=4))
            # for l in top: print(l)
            # for l in rows: print(l)
            # for l in bot: print(l)
            for l in combined: 
                bg,fg=None,None
                if l[0]=='Y': 
                    bg="#00ff00"
                    fg="#001100" 
                elif l[0]=='N':
                    bg="#ff0000"
                    fg="#110000"
                elif l[0]=='-':
                    bg="#110000"
                    fg="#551111"
                elif l[0]=='+':
                    bg="#001100"
                    fg="#115511" 
                print(l, bg=bg,fg=fg)

        else:
            # for l in top: printer.line(l)
            # for l in rows: printer.line(l)
            # for l in bot: printer.line(l)
            for l in combined: printer.line(l)
            printer.cut()


        

    def test(hostname,modules):
        good, bad, extra, missing  = {}, {}, {}, {}

        for k, v in modules.items():
            to_check = {"version": v["fw"], "mod": v["mod_func"]}
            stored = ModuleSettings[k]

            print(f"[{k}]")

            if not stored: extra[k] = v
            elif stored==to_check: good[k] = v
            else: bad[k] =v

        for k in ModuleSettings.get_keys():
            if k not in modules:
                missing[k] = ModuleSettings[k]

        print(good)
        print(bad)
        print(missing)
        print(extra)

        
class MAIN():
    __interval_thread_started = False
    def __init__(self):
        self.devices = set([])
        self.splashed = set()
        self.attempts = {}

    def no_bueno(self,ip):
        self.attempts[ip] = self.attempts.get(ip, 0) + 1
        if self.attempts[ip] >= 6:
            print(f"[{ip}] gonna stop trying", fg="#ff0000")
            self.devices.add(ip)

    def meter_scan(self):
        devices = set(get_devices())
        fresh = devices - self.devices
        stale = self.devices - devices

        # print(f"fresh: {fresh}")
        # print(f"stale: {stale}")

        for ip in stale:
            self.devices.discard(ip)

        for ip in fresh:
            try:
                meter = SSHMeter(ip)
                if (splash:=meter.in_splash()):
                    self.splashed.add(ip)
                    print(f"[{ip}] in splash!", fg="#ffff99")
                    continue

                try:
                    meter.connect()
                    if (ip in self.splashed): 
                        time.sleep(2)
                        self.splashed.discard(ip)
                    modules = meter.get_module_info()
                    hostname = meter.get_hostname()
                    meter.close()
                    printer.open()
                    zebra.organizedv2(hostname,modules)
                    print(f"[{ip}] successfully printed!", fg="#008800")
                    self.devices.add(ip)

                except (FilePrinter.FilePrinterNoAccess, FilePrinter.FilePrinterNotFound) as e:
                    print(f"[{ip}] couldn't connect to printer", fg="#880000")
                    self.no_bueno(ip)
                except:
                    print(f"[{ip}] failed to get info!", fg="#880000")
                    self.no_bueno(ip)

                finally:
                    try: printer.close()
                    except: pass

            except:
                print(f"[{ip}] is probably not a meter!", fg="#880000")
                self.no_bueno(ip)
                


    def run(self):
        count = 0 
        printer_connected = os.path.exists('/dev/usb/lp0')
        while True:
            # reset every 24hr
            if (count := count + 1) >= 86400: count = 0
            try:
                # if count % 2: 
                    # self.meter_scan()
                self.meter_scan()

                # 10 minute
                if count % 600:
                    pass
            except:
                pass
            time.sleep(1)

    def run_thread(self):
        if not MAIN.__interval_thread_started:
            threading.Thread(target=self.run, daemon=True).start()
            MAIN.__interval_thread_started = True



if __name__ == "__main__":
    # try:
    #     # APP().meter_scan()
    #     MAIN().run()
    # except KeyboardInterrupt: 
    #     print("goodbye")
    # except Exception as e:
    #     print(e)

    # MAIN().run_thread()
    # print(">> main meter->print thread started", fg="#00ffff")
    # input("")


    meter = 33
    # hostname = f"192.168.169.{meter}"
    hostname = "<meterId here>"
    with open(f"/app/lib/config/{meter}.json") as f:
        modules = json.load(f)

    # meter = SSHMeter("192.168.169.10")
    # modules = meter.get_module_info()
    # hostname = meter.get_hostname()

    printer.open()
    zebra.organizedv2(hostname,modules)
    printer.close()
    