#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import argparse
import sys

parser = argparse.ArgumentParser(
        description="This program is intent for cloning repositories of students"
            )

parser.add_argument("--config",
                    dest="config_file",
                    required=False, 
                    default="etc/studs_repos.conf",
                    help="File with configuration"
                    )

parser.add_argument("--action",
                    dest="action",
                    required=False,
                    default="pull",
                    help="action with git repository"
                                                                                                            )

args=parser.parse_args()

file_options=open(args.config_file)


options=dict()
for record in file_options:
    record=record.strip()
    if record != "" and record[0] == '#':
        continue
    opt=record.split('=')
    if len(opt) == 2 :
        options[opt[0].strip()]=opt[1].strip(' \n')

file_options.close()

print options




file_d=open(options["students_logins"],"r")


if args.action == "clone":
    if not  os.path.exists("src"):
        os.mkdir("src")

    for login in file_d:
        login=login.strip()
        print "begin work for  \"%s\" ---->" % login
        command_line="git clone ssh://%s\@%s/home/%s/repos src/%s" %\
        (
            options["remote_user"],
            options["host"],
            login,
            login
        )
        os.system(command_line)
        print "finish work for \"%s\" <----\n\n" % login

if args.action == "pull" or args.action == "push":
    for login in file_d:
        login=login.strip()
        print "begin work for  \"%s\" ---->" % login
        command_line="cd src/%s; git %s; cd .." % (login, args.action)
        os.system(command_line)
        print "finish work for \"%s\" <----\n\n" % login

file_d.close()


