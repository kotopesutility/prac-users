#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import hashlib
from datetime import date


parser = argparse.ArgumentParser(
        description=\
                """
                This program removes students from machine. 
                It generates archive with homes, requires file with logins in  input.
                """
                )

parser.add_argument('--logins',dest='logins', required=True, help="list of logins each login in newline.")
parser.add_argument('--archive',dest='archive', required=True, help="Name of archive where homes will stored .tar.gz will append to name.")

args=parser.parse_args()

if os.geteuid() != 0:
    print "You need root permissions to execute this script"
    sys.exit(1)


logins_file_d=open(args.logins)

tmp_fd=os.open(args.archive+".tar",os.O_CREAT|os.O_EXCL,0600)
os.close(tmp_fd)
os.system("/bin/tar --create --file %s.tar %s" % (args.archive, args.logins))

for student in logins_file_d:

    words=student.split(":")
    
    #
    # last word
    #
    student=words[-1]
    student=student.strip('"\n\r\t ')

    command_line="/bin/tar --remove-files --append --file %s.tar ~%s" %( args.archive, student )
    os.system(command_line)

    os.system("/usr/sbin/userdel %s" % ( student ))
    os.system("/usr/sbin/groupdel %s" % ( student ))
   
    print "User: %s deleted" % ( student )

logins_file_d.close()

print "Now compressing %s" % (args.archive)
os.system("gzip --best %s.tar" % (args.archive))

