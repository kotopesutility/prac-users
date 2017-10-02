#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import hashlib
from datetime import date


parser = argparse.ArgumentParser(description="This program register students on machine. It uses .csv file as input.")
parser.add_argument('--csv',dest='csv_file', required=True, help="File name with list of students in .csv format. Fields must be delimited by ':', and strings in \"\".")
parser.add_argument('--teachers',dest='teachers', required=True, help="List of teachers coma delimited")
parser.add_argument('--passwords',dest='passw_file', required=True, help="File where passwords are stored")
parser.add_argument("--comment", dest='comment', required=False, default="", help="Special comment string which describes group of students")

args=parser.parse_args()

if os.geteuid() != 0:
    print "You need root permissions to execute this script"
    sys.exit(1)


csv_file_d=open(args.csv_file)

passw_file=open(args.passw_file,"w")
os.chmod(args.passw_file,0600)

tmp_passwd_file=open("/tmp/foo","w")
os.chmod("/tmp/foo",0600)

hash_salt_file=open("/dev/random","r")
hash_salt=hash_salt_file.read(60)
hash_salt_file.close()


new_str=""
for i in xrange(0,60):
    new_str += chr(ord(hash_salt[i]) % (60-30) + 31)


my_hash=hashlib.sha1()
today=date.today()
hash_salt=today.ctime()+new_str
my_hash.update(hash_salt)


teachers=args.teachers.split(',')

for student in csv_file_d:
    attrs=student.split(':')
    full_name=attrs[0].strip('"')
    full_name=full_name.strip()
    email=attrs[1].strip('"')
    email=email.strip()
    login=attrs[2].strip()
    login=login.strip('"')


    my_hash.update(login+full_name)
    password=my_hash.hexdigest()[0:12]
    passw_file.write("\"%s\":\"%s\":\"%s\"\n" % (full_name, login, password))
    tmp_passwd_file.write("%s:%s\n" % (login, password))
    
    command_line="/usr/sbin/useradd --user-group --comment \"%s,,,%s; %s\" --create-home --shell /bin/bash %s" %\
    (
        full_name,
        email,
        args.comment,
        login            
    )
    os.system(command_line)
#   os.system("echo passwd -e %s" % (login))
    os.system("chmod -R o-rwx ~%s" % login )
    
    for teacher in teachers:
        os.system("/usr/sbin/usermod -a -G %s %s" % (login,teacher) )
    
    print "User: %s \"%s\" created\n" % (login, full_name)

tmp_passwd_file.close()
print "Changing passwords"
os.system("chpasswd < /tmp/foo")
os.unlink("/tmp/foo")

csv_file_d.close()
passw_file.close()    



