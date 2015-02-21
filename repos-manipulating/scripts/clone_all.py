#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os;

file_d=open("etc/logins.txt","r")
host="some.where.net"
remote_user="somebody"



os.mkdir("src")


for login in file_d:
    login=login.strip()
    command_line="git clone ssh://%s\@%s/home/%s/repos src/%s" %\
    (
        remote_user,
        host,
        login,
        login
    )
    os.system(command_line);

file_d.close()


