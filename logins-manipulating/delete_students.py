#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import hashlib
from datetime import date


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
        description=\
                """
                This program removes students from machine. 
                It generates archive with homes, requires file with logins in  input.
                """
                )

    parser.add_argument(
            '--logins',
            dest='logins',
            required=True,
            help="list of logins each login in newline."
            )

    parser.add_argument(
            '--archive',
            dest='archive',
            required=False,
            default="",
            help="Name of archive where homes will stored .tar.gz will append to name."
            )

    args=parser.parse_args(arguments_list[1:])

    if os.geteuid() != 0:
        print "You need root permissions to execute this script"
        return 1


    logins_file_d=open(args.logins)

    if args.archive == "":
        args.archive="homes_%s" % os.path.splitext(args.logins)[0]

    tmp_fd=os.open(args.archive+".tar",os.O_CREAT|os.O_EXCL,0600)
    os.close(tmp_fd)
    os.system("/bin/tar --create --file %s.tar %s" % (args.archive, args.logins))

    for student_string in logins_file_d:
        student=parse_student_string(student_string)                                                
        if student == None:                                                                         
            continue
    
        login=student[2]
        name=student[0]

        command_line="/bin/tar --remove-files --append --file %s.tar ~%s" %( args.archive, login )
        os.system(command_line)

        os.system("/usr/sbin/userdel %s" % ( login ))
        os.system("/usr/sbin/groupdel %s" % ( login ))
   
        print "User: %s (%s) deleted" % ( login, name )

    logins_file_d.close()

    print "Now compressing %s" % (args.archive)
    os.system("gzip --best %s.tar" % (args.archive))
    
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

