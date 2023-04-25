# qemu_vm
Small QEMU Virtual Machine Management Tool

## Usage

### create new vm image from iso file
```bash
./vm.py create_from_iso mydebian 16 debian-10.13.0-amd64-xfce-CD-1.iso
```
Will create a 16 GB disk file and start a new qemu vm for os installation
with debian-10.13.0-amd64-xfce-CD-1.iso image

### create new vm image from predefined distribution (debian or ubuntu)
```bash
./vm.py create mydebian 16 debian
```
Will create a 16 GB disk file, download the predefined debian iso file
and start a new qemu vm for os installation.

### start vm (need an installed qemu image)
```bash
./vm.py start upmem-vm-debian10.13.qcow  --daemonize --ssh_port 9134
```

Will start a new vm from upmem-vm-debian10.13.qcow image in the background
and expose ssh port 9134.

## configurre a new vm (eg debian-10.13)

If no ssh server is installed on the vm (default), you should
start the vm in graphical mode.

```bash
  ./vm.py start upmem-vm-debian10.13.qcow --graphical
```

set the user as root
```bash
  usermod -aG sudo {USER}
```

install ssh server on vm (eg ubuntu-10.04)

install openssh-server
```bash
sudo apt install openssh-server
```

Then, you can restart the machine on non-graphical mode (default),
and connect through ssh.

```bash
./vm.py start upmem-vm-debian10.13.qcow  --daemonize --ssh_port 9134
ssh {USER}@localhost -p 9134
```

## start the vm with an additional disk

as example, to create a new disk of 32 GB
```bash
qemu-img create -f qcow2 mydisk.qcow2 32G
```

start the machine with the new disk attached

```bash
./vm.py start upmem-vm-debian10.13.qcow  --daemonize --ssh_port 9134 --disk mydisk.qcow2
ssh {USER}@localhost -p 9134
```
Normally, the new disk is visible in /dev/vdb,
you can check that your disk is visible with 
```bash
fdisk -l
```

the first time, you need to create create a new partition on the new disk (eg ext4)
```bash
sudo mkfs -t ext4 /dev/vdb
```

then, you can mount it manually on specific directory (eg : /data) :
```bash
sudo mkdir /data && sudo chown {USER}:{GOUP} /data
sudo mount /dev/vdb /data
```

or configure the fstab as below for a permanent mounting point :
```bash
sudo echo "/dev/vdb /data ext4 rw,user,auto,exec 0 0" >>  /etc/fstab
```

# Apendix

## update debian10 packages list (buster)

add this to /etc/apt/sources.list

```bash
deb-src http://deb.debian.org/debian/ buster main

deb http://security.debian.org/debian-security buster/updates main
deb-src http://security.debian.org/debian-security buster/updates main

# buster-updates, previously known as 'volatile'
deb http://deb.debian.org/debian/ buster-updates main
deb-src http://deb.debian.org/debian/ buster-updates main

deb-src http://deb.debian.org/debian/ sid main contrib non-free
```
## disable password for USER

```bash
sudo visudo
```

add thoses lines :

```bash
{USER}  ALL=(ALL) NOPASSWD:ALL
```



