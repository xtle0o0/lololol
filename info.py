import subprocess
import os
import json

def get_system_info():
    hostname = subprocess.getoutput("hostname").strip()
    device_username = subprocess.getoutput("whoami").strip()
    os_info = subprocess.getoutput("lsb_release -d | awk -F': ' '{print $2}'").strip()
    kernel = subprocess.getoutput("uname -r").strip()
    uptime = subprocess.getoutput("uptime -p").strip()
    public_ip = subprocess.getoutput("curl -s ifconfig.me").strip()
    location = subprocess.getoutput(f"curl -s ipinfo.io/{public_ip}").strip()
    shell = os.getenv('SHELL', 'N/A')
    current_directory = os.getcwd()
    cpu_info = subprocess.getoutput("lscpu | grep 'Model name' | awk -F': ' '{print $2}'").strip()
    memory_info = subprocess.getoutput("free -h | grep 'Mem:' | awk '{print $2}'").strip()
    disk_usage = subprocess.getoutput("df -h --output=source,size | grep -v 'Filesystem'").strip()
    network_info = subprocess.getoutput("ip -o -4 addr list | awk '{print $4}'").strip()
    last_boot = subprocess.getoutput("who -b | awk '{print $3, $4}'").strip()
    process_count = subprocess.getoutput("ps aux | wc -l").strip()
    systemd_version = subprocess.getoutput("systemctl --version | head -n1").strip()

    with open("/tmp/system_info.txt", "w") as file:
        file.write(f"🌐 Hostname: {hostname}\n")
        file.write(f"👤 Device Username: {device_username}\n")
        file.write(f"🖥 OS: {os_info}\n")
        file.write(f"🖧 Kernel: {kernel}\n")
        file.write(f"⏳ Uptime: {uptime}\n")
        file.write(f"🌍 Public IP: {public_ip}\n")
        file.write(f"📍 Location: {location}\n")
        file.write(f"🔐 Shell: {shell}\n")
        file.write(f"📂 Current Directory: {current_directory}\n")
        file.write(f"🖥 CPU Info: {cpu_info}\n")
        file.write(f"🧠 Memory Info: {memory_info}\n")
        file.write(f"💾 Disk Usage:\n{disk_usage}\n")
        file.write(f"🌐 Network Info:\n{network_info}\n")
        file.write(f"🔄 Last Boot: {last_boot}\n")
        file.write(f"🧩 Process Count: {process_count}\n")
        file.write(f"🔧 Systemd Version: {systemd_version}\n")

if __name__ == "__main__":
    get_system_info()
