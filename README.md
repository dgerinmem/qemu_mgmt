# qemu_vm
Small QEMU Virtual Machine Management Tool



# create new vm image from iso file
```bash
./vm.py create_from_iso mydebian 16 debian-10.13.0-amd64-xfce-CD-1.iso
```
Will create a 16 GB disk file and start a new qemu vm for os installation
with debian-10.13.0-amd64-xfce-CD-1.iso image

# create new vm image from predefined distribution (debian or ubuntu)
```bash
./vm.py create mydebian 16 debian
```
Will create a 16 GB disk file, download the predefined debian iso file
and start a new qemu vm for os installation.

# start vm (need an installed qemu image)
```bash
./vm.py start upmem-vm-debian10.13.qcow  --daemonize --ssh_port 9134
```

Will start a new vm from upmem-vm-debian10.13.qcow image in the background
and expose ssh port 9134.
