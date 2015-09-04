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

    for student in file_d:
        words=student.split(":")
        #
        # last word
        #
        login=words[-1]
        login=login.strip()
        login=login.strip('"')
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
    for student in file_d:
        words=student.split(":")
        #
        # last word
        #
        login=words[-1]
        login=login.strip()
        login=login.strip('"')
        print "begin work for  \"%s\" ---->" % login
        command_line="cd src/%s; git %s; cd .." % (login, args.action)
        os.system(command_line)
        print "finish work for \"%s\" <----\n\n" % login

if args.action == "add-to-trac":
    for student in file_d:
        words=student.split(":")
        #
        # last word
        #
        login=words[-1]
        login=login.strip()
        login=login.strip('"')
         
        command_line="trac-admin %s repository add %s-%s %s/src/%s/.git git" %\
                (
                        options["trac_env_path"],
                        options["group_prefix"],
                        login,
                        os.getcwd(), 
                        login
                )
        print "begin add  \"%s\" to trac" % login
        os.system(command_line)
        print "finish add \"%s\" to trac\n\n" % login

if args.action == "remove-from-trac":
    for student in file_d:
        words=student.split(":")
        #
        # last word
        #
        login=words[-1]
        login=login.strip()
        login=login.strip('"')
        
        command_line="trac-admin %s repository remove %s-%s" %\
                (
                        options["trac_env_path"],
                        options["group_prefix"],
                        login
                )
        print "begin remove from  \"%s\" trac" % login
        os.system(command_line)
        print "finish remove from \"%s\" trac\n\n" % login


file_d.close()


