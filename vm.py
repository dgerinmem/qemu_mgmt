#!/usr/bin/python3

# Copyright 2023 UPMEM. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

r"""UPMEM QEMU Virtual Machine Management Tool
"""

import argparse
import subprocess
from enum import Enum
import socket
import os
import psutil

debian = "debian"
ubuntu = "ubuntu"

distbibutions = [debian, ubuntu]

iso_paths = {debian: "debian-10.13.0-amd64-xfce-CD-1.iso",
             ubuntu: "ubuntu-20.04.3-live-server-amd64.iso"
             }

iso_urls = {debian: "https://cdimage.debian.org/cdimage/archive/10.13.0/amd64/iso-cd/debian-10.13.0-amd64-xfce-CD-1.iso",
            ubuntu: "https://releases.ubuntu.com/focal/ubuntu-20.04.6-desktop-amd64.iso"
            }


def download_iso(dist):
    if dist in iso_paths:
        cmd = f"wget {iso_urls[dist]} -O {iso_paths[dist]}"
        subprocess.call(cmd, shell=True)
    else:
        print("Distribution not supported")


def iso_exists(dist):
    if dist in iso_paths:
        return os.path.exists(iso_paths[dist])
    else:
        return False


def get_available_port():
    port = 3132
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result == 0:
            print("Port {} is already in use".format(port))
            port = port + 1
            continue
        else:
            print("Port {} is available".format(port))
            return port


def create_vm_from_iso(name, size, iso_path):
    img_path = f"{name}.size{size}G.qcow2"
    cmd1 = f"qemu-img create -f qcow2 {img_path} {size}G"
    cmd2 = f"qemu-system-x86_64 -enable-kvm -hda {img_path} -cdrom {iso_path} -m 4000 -boot d -net user -net nic,model=ne2k_pci -enable-kvm"
    subprocess.call(cmd1, shell=True)
    subprocess.call(cmd2, shell=True)


def create_vm(name, size, dist):
    if dist in distbibutions:
        if not iso_exists(dist):
            download_iso(dist)
        create_vm_from_iso(name, size, iso_paths[dist])
    else:
        print("Distribution not supported")


def start_vm(img_path, ssh_port, mem_size, daemonize, disk, dump_cmd):
    # TODO it works, but we should use another port than sh_port for vnc
    # get_available_port() does not work as expected, it never sees vnc port open
    # port = get_available_port()
    # WORKAROUND port = ssh_port + 1
    port = ssh_port + 1
    nproc = int(os.cpu_count()/2)

    cmd = f"qemu-system-x86_64 -vnc 127.0.0.1:{port} \
                                -smp {nproc} \
                                -device virtio-net,netdev=user.0 \
                                -m {mem_size} \
                                -drive file={img_path},if=virtio,index=0,cache=writeback,discard=ignore,format=qcow2 \
                                -machine type=pc,accel=kvm \
                                -netdev user,id=user.0,hostfwd=tcp::{ssh_port}-:22"

    if daemonize:
        cmd = cmd + " --daemonize"

    print(disk)
    if disk != None:
        cmd = cmd + \
            " -drive file={},if=virtio,index=1,cache=writeback,discard=ignore,format=qcow2".format(
                disk)

    if dump_cmd:
        print(cmd)

    if subprocess.call(cmd, shell=True) == 0:
        print("vm started wih ssh port", ssh_port, "on localhost",
              "connect with \nssh -p", ssh_port, "{USER}@localhost")
    else:
        print("vm failed to start")


def stop_vm(name):
    cmd = f"pkill -f {name}"
    subprocess.call(cmd, shell=True)


parser = argparse.ArgumentParser(
    description="QEMU Virtual Machine Management Tool")
subparsers = parser.add_subparsers()

create_parser = subparsers.add_parser(
    "create_from_iso", help="Create a new virtual machine from an ISO file")
create_parser.add_argument(
    "name", type=str, help="Name of the virtual machine")
create_parser.add_argument(
    "size", type=int, help="Size of the virtual machine disk in GB")
create_parser.add_argument("iso_path", type=str, help="Path to the ISO file")
create_parser.set_defaults(func=create_vm_from_iso)

create_parser = subparsers.add_parser(
    "create", help="Create a new virtual machine")
create_parser.add_argument(
    "name", type=str, help="Name of the virtual machine")
create_parser.add_argument(
    "size", type=int, help="Size of the virtual machine disk in GB")
create_parser.add_argument(
    "distrib", type=str, help="Distribution of the virtual machine")
create_parser.set_defaults(func=create_vm)


start_parser = subparsers.add_parser("start", help="Start a virtual machine")
start_parser.add_argument("img_path", type=str,
                          help="Path to the virtual machine image")
start_parser.add_argument("--ssh_port", type=int,
                          default=2222, help="SSH port for the virtual machine")
start_parser.add_argument("--mem_size", type=int, default=16000,
                          help="Memory size for the virtual machine in MB")
start_parser.add_argument("--disk", type=str, default=None,
                          help="Attach an additional disk to the virtual machine",)
start_parser.add_argument(
    "-d", "--daemonize", action="store_true", help="daemonize virtual machine")
start_parser.add_argument(
    "--dump_cmds", action="store_true", help="dump qemu commands")
start_parser.set_defaults(func=start_vm)

args = parser.parse_args()

if hasattr(args, "func"):
    if args.func == create_vm_from_iso:
        create_vm_from_iso(args.name, args.size, args.iso_path)
    if args.func == create_vm:
        create_vm(args.name, args.size, args.distrib)
    if args.func == start_vm:
        start_vm(args.img_path, args.ssh_port, args.mem_size,
                 args.daemonize, args.disk, args.dump_cmds)

else:
    parser.print_help()
