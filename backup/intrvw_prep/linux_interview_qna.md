# Linux Interview Q&A

# Linux Overview

Linux is an open-source operating system kernel used in servers, embedded systems, networking equipment, cloud infrastructure, Android devices, and supercomputers. It manages hardware resources such as CPU, memory, storage, and devices while allowing applications and users to interact with the system.

## Important Linux Topics (Plain English)

### 1. Kernel
The kernel is the core of Linux. It manages:
- CPU scheduling
- Memory allocation
- File systems
- Device drivers
- Process management

### Example
When you open a file, the kernel communicates with the storage device and returns the file data to your program.

---

### 2. Shell
The shell is the command-line interface used to interact with Linux.

Common shells:
- bash
- zsh
- sh

### Example
```bash
ls -l
```
Lists files in long format.

---

### 3. File System
Linux treats everything as a file.

Important directories:
- `/home` → user files
- `/etc` → configuration files
- `/bin` → essential commands
- `/var` → logs and variable data
- `/proc` → process/kernel information

### Example
```bash
cat /proc/cpuinfo
```
Displays CPU information.

---

### 4. Processes and Threads
A process is a running program.
A thread is a lightweight execution unit inside a process.

### Example
```bash
ps -ef
```
Displays running processes.

---

### 5. Permissions
Linux uses read/write/execute permissions.

### Example
```bash
chmod 755 file.sh
```
Makes script executable.

---

### 6. Memory Management
Linux manages:
- RAM
- virtual memory
- swap
- caching

### Example
```bash
free -h
```
Shows memory usage.

---

### 7. Networking
Linux provides networking tools for:
- routing
- sockets
- interfaces
- packet analysis

### Example
```bash
ip addr
```
Shows network interfaces.

---

### 8. Device Drivers
Drivers allow Linux to communicate with hardware.

### Example
USB keyboard driver handling keyboard input.

---

### 9. Signals
Signals are notifications sent to processes.

### Example
```bash
kill -9 PID
```
Forcefully terminates a process.

---

### 10. System Calls
Applications communicate with the kernel using system calls.

### Example
```c
open(), read(), write(), fork()
```

---

### 11. IPC (Inter Process Communication)
Processes communicate using:
- pipes
- shared memory
- message queues
- sockets

### Example
```bash
ls | grep txt
```
Pipe connects two commands.

---

### 12. Boot Process
Linux boot flow:
1. BIOS/UEFI
2. Bootloader (GRUB)
3. Kernel
4. init/systemd
5. User space

---

### 13. Embedded Linux
Linux is widely used in:
- routers
- telecom equipment
- automotive systems
- IoT devices

### Example
OpenWRT router firmware.

---

### 14. Scheduling
Linux scheduler decides which process gets CPU time.

### Example
Real-time scheduling in telecom base stations.

---

### 15. Logging
Linux logs system events.

### Example
```bash
tail -f /var/log/syslog
```
Monitors live logs.

---

# Top 30 Linux Interview Questions and Answers

## 1. What is Linux?
Linux is an open-source Unix-like operating system kernel used in servers, embedded systems, and desktops.

---

## 2. What is the Linux kernel?
The kernel is the core part of Linux responsible for managing hardware, memory, processes, and system calls.

---

## 3. What is the difference between a process and a thread?
A process has its own memory space, while threads share memory within the same process.

---

## 4. What is a zombie process?
A zombie process is a terminated process whose exit status has not yet been collected by its parent.

---

## 5. What is an orphan process?
An orphan process is a process whose parent has terminated.

---

## 6. What is the purpose of `fork()`?
`fork()` creates a new child process by duplicating the current process.

---

## 7. What is `exec()`?
`exec()` replaces the current process image with a new program.

---

## 8. What is a system call?
A system call is an interface between user applications and the Linux kernel.

---

## 9. What is virtual memory?
Virtual memory allows processes to use more memory than physically available using disk swap space.

---

## 10. What is swap memory?
Swap memory is disk space used when RAM becomes full.

---

## 11. What is the difference between hard link and soft link?
Hard links point to the same inode, while soft links are shortcut files pointing to another path.

---

## 12. What is an inode?
An inode stores metadata about a file such as permissions, owner, and disk block locations.

---

## 13. What is the difference between `kill` and `kill -9`?
`kill` sends SIGTERM for graceful termination, while `kill -9` forcefully kills the process using SIGKILL.

---

## 14. What is the purpose of `chmod`?
`chmod` changes file permissions.

Example:
```bash
chmod 755 script.sh
```

---

## 15. What does `grep` do?
`grep` searches text patterns in files.

Example:
```bash
grep error log.txt
```

---

## 16. What is a shell script?
A shell script is a text file containing Linux commands executed sequentially.

---

## 17. What is piping in Linux?
Piping passes output from one command as input to another command.

Example:
```bash
ls | grep txt
```

---

## 18. What is the difference between `>` and `>>`?
`>` overwrites a file, while `>>` appends to a file.

---

## 19. What is SSH?
SSH is a secure protocol used for remote login and command execution.

---

## 20. What is the purpose of `top`?
`top` displays running processes and system resource usage.

---

## 21. What is `ps -ef` used for?
It displays detailed information about running processes.

---

## 22. What is the difference between user mode and kernel mode?
User mode has restricted access, while kernel mode has full hardware access.

---

## 23. What is a daemon process?
A daemon is a background service process.

Example:
```text
sshd
```

---

## 24. What is `/proc`?
`/proc` is a virtual filesystem providing process and kernel information.

---

## 25. What is the purpose of `dmesg`?
`dmesg` displays kernel boot and driver messages.

---

## 26. What is the difference between ext4 and FAT32?
ext4 supports permissions and journaling, while FAT32 is simpler and more portable.

---

## 27. What is a file descriptor?
A file descriptor is a number used by Linux to identify open files.

---

## 28. What are environment variables?
Environment variables store configuration values used by processes.

Example:
```bash
echo $PATH
```

---

## 29. What is the purpose of `netstat` or `ss`?
They display network connections and listening ports.

---

## 30. What is `systemd`?
`systemd` is the Linux init system responsible for booting and managing services.

---

# Bonus Linux Commands

```bash
ls        # list files
pwd       # print current directory
cd        # change directory
cp        # copy files
mv        # move/rename files
rm        # remove files
cat       # display file contents
find      # search files
free -h   # memory usage
df -h     # disk usage
top       # process monitor
```

---

# Final Interview Tips

- Understand processes, memory, and file systems clearly.
- Practice Linux commands daily.
- Learn debugging tools like:
  - gdb
  - strace
  - valgrind
- Be comfortable with shell scripting.
- Understand basic networking and IPC.

---

# One-Line Linux Summary

Linux is an open-source operating system kernel that manages hardware resources, processes, memory, files, networking, and system services while providing interfaces for applications and users.

