import subprocess
import time
import os
import sys
import re

try:
    from colorama import init, Fore, Style
    init()
    COLOR = True
except ImportError:
    COLOR = False

try:
    import requests
except ImportError:
    requests = None

def c(text, color):
    if COLOR:
        return color + text + Style.RESET_ALL
    return text

def slow_print(text, delay=0.02):
    for c_ in text:
        print(c_, end='', flush=True)
        time.sleep(delay)
    print()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_header():
    clear()
    print(c(r""" 
 __      __._____________.__         __________                                   
/  \    /  \__\_   _____/|__|        \______   \ ____ _____  ______   ___________ 
\   \/\/   /  ||    __)  |  |  ______ |       _// __ \\__  \ \____ \_/ __ \_  __ \
 \        /|  ||     \   |  | /_____/ |    |   \  ___/ / __ \|  |_> >  ___/|  | \/
  \__/\  / |__|\___  /   |__|         |____|_  /\___  >____  /   __/ \___  >__|   
       \/          \/                        \/     \/     \/|__|        \/       
    """, Fore.LIGHTCYAN_EX))
    print(c("                WiFiReaper v4.0 - By Aju", Fore.LIGHTGREEN_EX))
    print(c("                LEGAL Wi-Fi Password & Info Toolkit\n", Fore.LIGHTBLACK_EX))

def check_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def request_admin():
    if not check_admin():
        try:
            import ctypes
            print("[*] Requesting administrator privileges...")
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            if result > 32:
                sys.exit(0)
            else:
                print("[!] Failed to elevate privileges.")
                print("[!] Continuing with limited functionality...")
                time.sleep(2)
                return False
        except Exception as e:
            print(f"[!] Failed to elevate privileges: {str(e)}")
            print("[!] Continuing with limited functionality...")
            time.sleep(2)
            return False
    return True

def grab_wifi_passwords(export=False):
    slow_print("[*] Grabbing all saved Wi-Fi passwords...\n")
    try:
        output = subprocess.check_output("netsh wlan show profiles", shell=True, stderr=subprocess.DEVNULL).decode(errors="ignore")
        profiles = [line.split(":")[1].strip() for line in output.splitlines() if "All User Profile" in line]
        if not profiles:
            print("[!] No saved Wi-Fi profiles found.")
            return
        print(f"[+] Found {len(profiles)} saved profile(s)\n")
        print("-" * 60)
        print(f"{'Network Name':<30} | {'Password'}")
        print("-" * 60)
        found_passwords = 0
        results = []
        for profile in profiles:
            try:
                info = subprocess.check_output(
                    f'netsh wlan show profile name="{profile}" key=clear',
                    shell=True, stderr=subprocess.DEVNULL
                ).decode(errors="ignore")
                password = "No password stored"
                for line in info.splitlines():
                    if "Key Content" in line:
                        password = line.split(":", 1)[1].strip()
                        if password:
                            found_passwords += 1
                        break
                display_name = profile[:29] + "..." if len(profile) > 29 else profile
                print(f"{display_name:<30} | {password}")
                results.append(f"{display_name:<30} | {password}")
            except subprocess.CalledProcessError:
                print(f"{profile:<30} | Error reading profile")
                results.append(f"{profile:<30} | Error reading profile")
        print("-" * 60)
        print(f"[+] Retrieved passwords for {found_passwords} network(s)")
        if export:
            with open("wifi_passwords.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(results))
            print(c("[+] Results exported to wifi_passwords.txt", Fore.LIGHTYELLOW_EX))
    except subprocess.CalledProcessError:
        print("[!] Error: Unable to access Wi-Fi profiles. Run as administrator.")
    except Exception as e:
        print(f"[!] Unexpected error: {str(e)}")

def scan_nearby_networks(export=False):
    slow_print("[*] Scanning for nearby Wi-Fi networks...\n")
    try:
        output = subprocess.check_output("netsh wlan show networks mode=bssid", shell=True, stderr=subprocess.DEVNULL).decode(errors="ignore")
        networks = []
        current = {}
        for line in output.splitlines():
            ssid_match = re.match(r"\s*SSID\s+\d+\s+:\s(.+)", line)
            if ssid_match:
                if current:
                    networks.append(current)
                current = {"SSID": ssid_match.group(1)}
            bssid_match = re.match(r"\s*BSSID\s+\d+\s+:\s(.+)", line)
            if bssid_match and current is not None:
                current["BSSID"] = bssid_match.group(1)
            signal_match = re.match(r"\s*Signal\s+:\s(.+)", line)
            if signal_match and current is not None:
                current["Signal"] = signal_match.group(1)
            channel_match = re.match(r"\s*Channel\s+:\s(.+)", line)
            if channel_match and current is not None:
                current["Channel"] = channel_match.group(1)
            auth_match = re.match(r"\s*Authentication\s+:\s(.+)", line)
            if auth_match and current is not None:
                current["Auth"] = auth_match.group(1)
        if current:
            networks.append(current)
        if not networks:
            print("[!] No networks found. Is your Wi-Fi adapter enabled?")
            return
        print("-" * 100)
        print(f"{'SSID':<25} | {'BSSID':<20} | {'Signal':<8} | {'Channel':<7} | {'Auth'}")
        print("-" * 100)
        results = []
        for net in networks:
            ssid = net.get("SSID", "")
            bssid = net.get("BSSID", "")
            signal = net.get("Signal", "")
            channel = net.get("Channel", "")
            auth = net.get("Auth", "")
            print(f"{ssid[:24]:<25} | {bssid:<20} | {signal:<8} | {channel:<7} | {auth}")
            results.append(f"{ssid[:24]:<25} | {bssid:<20} | {signal:<8} | {channel:<7} | {auth}")
        print("-" * 100)
        print(f"[+] Found {len(networks)} network(s)")
        if export:
            with open("wifi_nearby.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(results))
            print(c("[+] Results exported to wifi_nearby.txt", Fore.LIGHTYELLOW_EX))
    except subprocess.CalledProcessError:
        print("[!] Error: Unable to scan networks. Check if Wi-Fi adapter is enabled.")
    except Exception as e:
        print(f"[!] Unexpected error: {str(e)}")

def show_current_wifi():
    slow_print("[*] Getting current Wi-Fi connection details...\n")
    try:
        output = subprocess.check_output("netsh wlan show interfaces", shell=True, stderr=subprocess.DEVNULL).decode(errors="ignore")
        print(output)
    except Exception as e:
        print(f"[!] Error: {str(e)}")

def connect_to_wifi():
    profile = input("Enter the Wi-Fi profile name to connect: ").strip()
    if not profile:
        print("[!] No profile entered.")
        return
    try:
        subprocess.run(f'netsh wlan connect name="{profile}"', shell=True, check=True)
        print(f"[+] Attempted to connect to '{profile}'.")
    except Exception as e:
        print(f"[!] Error: {str(e)}")

def disconnect_wifi():
    slow_print("[*] Disconnecting from current Wi-Fi network...\n")
    try:
        subprocess.run("netsh wlan disconnect", shell=True, check=True)
        print("[+] Disconnected from Wi-Fi.")
    except Exception as e:
        print(f"[!] Error: {str(e)}")

def show_mac_address():
    slow_print("[*] Getting MAC address of Wi-Fi adapter...\n")
    try:
        output = subprocess.check_output('getmac /v /fo list', shell=True).decode(errors="ignore")
        print(output)
    except Exception as e:
        print(f"[!] Error: {str(e)}")

def show_adapter_info():
    slow_print("[*] Listing all network adapters...\n")
    try:
        output = subprocess.check_output('ipconfig /all', shell=True).decode(errors="ignore")
        print(output)
    except Exception as e:
        print(f"[!] Error: {str(e)}")

def show_public_ip():
    slow_print("[*] Getting your public IP address...\n")
    if requests is None:
        print("[!] Install requests: pip install requests")
        return
    try:
        ip = requests.get('https://api.ipify.org').text
        print(f"Your public IP address is: {ip}")
    except Exception as e:
        print(f"[!] Error: {str(e)}")

def ping_target():
    target = input("Enter website or IP to ping (e.g. google.com): ").strip()
    if not target:
        print("[!] No target entered.")
        return
    print(f"\n[*] Pinging {target}...\n")
    try:
        subprocess.run(f"ping {target}", shell=True)
    except Exception as e:
        print(f"[!] Error: {str(e)}")

def show_help():
    clear()
    show_header()
    print("WiFiReaper - LEGAL Wi-Fi Hacking Help\n")
    print("1. Grab all saved Wi-Fi passwords: Shows all Wi-Fi passwords stored on your PC.")
    print("2. Scan nearby Wi-Fi networks: See all Wi-Fi networks in range, with channel, signal, and security info.")
    print("3. Show your current Wi-Fi connection details: See info about your current connection.")
    print("4. Connect to a saved Wi-Fi profile: Connect to a Wi-Fi you've connected to before.")
    print("5. Disconnect from current Wi-Fi: Disconnect from your current Wi-Fi network.")
    print("6. Show MAC address of Wi-Fi adapter.")
    print("7. Show all network adapters.")
    print("8. Show your public IP address.")
    print("9. Ping a website or IP address.")
    print("10. Help: Show this help menu.")
    print("11. About: Show info about this tool.")
    print("0. Exit: Quit the program.")
    input("\nPress Enter to return to the menu...")

def show_info():
    clear()
    show_header()
    slow_print("About WiFiReaper v4.0")
    print("\nThis tool helps you:")
    print("• Grab all saved Wi-Fi passwords on your computer")
    print("• Scan for all nearby wireless networks (saved or not)")
    print("• Show your current Wi-Fi connection details")
    print("• Connect/disconnect to Wi-Fi profiles")
    print("• Show MAC address of Wi-Fi adapter")
    print("• Show all network adapters")
    print("• Show your public IP address")
    print("• Ping a website or IP address")
    print("• Learn about network security")
    print("\nNote: This tool only works on Windows systems")
    print("For best results, run as administrator")
    print("\nCreated for educational purposes only!")

def main():
    if not request_admin():
        return
    while True:
        show_header()
        slow_print("Select an option:")
        print("1. Grab all saved Wi-Fi passwords")
        print("2. Scan nearby Wi-Fi networks")
        print("3. Show your current Wi-Fi connection details")
        print("4. Connect to a saved Wi-Fi profile")
        print("5. Disconnect from current Wi-Fi")
        print("6. Show MAC address of Wi-Fi adapter")
        print("7. Show all network adapters")
        print("8. Show your public IP address")
        print("9. Ping a website or IP address")
        print("10. Help")
        print("11. About this tool")
        print("0. Exit")
        try:
            choice = input("\nEnter your choice (0-11): ").strip()
            if choice == "1":
                clear(); show_header(); grab_wifi_passwords()
            elif choice == "2":
                clear(); show_header(); scan_nearby_networks()
            elif choice == "3":
                clear(); show_header(); show_current_wifi()
            elif choice == "4":
                clear(); show_header(); connect_to_wifi()
            elif choice == "5":
                clear(); show_header(); disconnect_wifi()
            elif choice == "6":
                clear(); show_header(); show_mac_address()
            elif choice == "7":
                clear(); show_header(); show_adapter_info()
            elif choice == "8":
                clear(); show_header(); show_public_ip()
            elif choice == "9":
                clear(); show_header(); ping_target()
            elif choice == "10":
                show_help()
            elif choice == "11":
                show_info()
            elif choice == "0":
                slow_print("\nExiting WiFiReaper...")
                break
            else:
                slow_print("\n[!] Invalid choice. Please select 0-11.")
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            slow_print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n[!] Error: {str(e)}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)