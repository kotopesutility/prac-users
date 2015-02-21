#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os;

file_d=open("etc/logins.txt","r")
host="some.where.net"
remote_user="somebody"


for login in file_d:
    login=login.strip()
    command_line="cd src/%s; git pull; cd .." % (login)
    os.system(command_line);

file_d.close()


