#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import sys
import getpass 

def parse_opts(config_file):
    """
    Parse options from config file
    format:
    name = value
    with comments in shell style '#'
    """
    options=dict()
    
    #
    # set default options
    #
    options['remote_user']=getpass.getuser()
    options['students_logins']="/etc/students.csv"
    options['repository_way']="/home/%STUDENT_LOGIN%/repos"

    file_options=open(config_file)
    for record in file_options:
        record=record.strip()
        if record != "" and record[0] == '#':
            continue
        opt=record.split('=')
        if len(opt) == 2 :
            options[opt[0].strip()]=opt[1].strip(' \n')
    
    file_options.close()
    
    return options

def parse_student_string(student):
    """
    Very stupid parsing function.
    It splits by ':', then clear ".

    There no defence for:
       " \" "
    and for:
       "abc:fff":"gggg"
    it will be parse incorrect.
    """
    student = student.strip()

    if len(student) == 0:
        return None

    words=student.split(":")
    if len(words) != 3:
        return None
    
    full_name = words[0].strip().strip('"')
    email     = words[1].strip().strip('"')
    login     = words[2].strip().strip('"')

    return (full_name, email, login)


def main(arguments_list=None):
    """
    This is the main functions for repositories manipulating
    """
    
    if arguments_list == None:
        return 1

    parser = argparse.ArgumentParser(
            description="This program is maniputating with group of student's git repositories."
                        " For example performs multiple git clone.")
    
    parser.add_argument("--config",
                        dest="config_file",
                        required=False, 
                        default="etc/studs_repos.conf",
                        help="File with configuration"
                        )
    
    parser.add_argument("--action",
                        dest="action",
                        choices = ['clone','pull','push','add-to-trac','remove-from-trac'],
                        required=False,
                        default="pull",
                        help="Action with git repository"
                        )

    args=parser.parse_args(arguments_list[1:])

    options=parse_opts(args.config_file)
    print (options)
    
    
    
    
    file_d=open(options["students_logins"],"r")
    
    
    if args.action == "clone":
        if not  os.path.exists("src"):
            os.mkdir("src")
    
    for student_string in file_d:

        student=parse_student_string(student_string)
        if student == None:
            continue

        name  = student[0]
        login = student[2]

        command_line= ""
        
        print ("begin work for  \"(%s) %s\" ---->" % (name, login))

        if args.action == "clone":
            
                       
            remote_path=options["repository_way"].replace("%STUDENT_LOGIN%",login)
            command_line="git clone ssh://%s\@%s%s src/%s" %\
                         (
                              options["remote_user"],
                              options["host"],
                              remote_path,
                              login
                         )

        if args.action == "pull" or args.action == "push":
            command_line="cd src/%s; git %s; cd .." % (login, args.action)

        if args.action == "add-to-trac":      
            command_line="trac-admin %s repository add %s-%s %s/src/%s/.git git" %\
                    (
                            options["trac_env_path"],
                            options["group_prefix"],
                            login,
                            os.getcwd(), 
                            login
                    )

        if args.action == "remove-from-trac":
            command_line="trac-admin %s repository remove %s-%s" %\
                    (
                            options["trac_env_path"],
                            options["group_prefix"],
                            login
                    )

        os.system(command_line)
        print ("finish work for \"%s\" <----\n\n" % login)
   
    file_d.close()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

