#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import sys
import argparse
import hashlib
from datetime import date


def parse_csv(path, delimiter=":"):
    """
    This function parse giving .csv file and create dictionary acording
    with names from header as a dictionary.

    :param path: path to the .csv file
    :type path: str or pathlib.Path
    :param delimiter: delimiter used in .csv file
    :type delimiter: str
    :return: parsed .csv file
    :rtype: list of dictionaries
    """
    with open(path) as csv_file:
        reader = csv.reader(csv_file, delimiter=delimiter)
        keys = reader.__next__()
        return [{k: val for k, val in zip(keys, line)} for line in reader]


def main(arguments_list=None):
    """
    This is the main functions for repositories manipulating
    """

    if arguments_list is None:
        return 1

    parser = argparse.ArgumentParser(
            description="This program register students on machine."
                        " It uses .csv file as input."
            )

    parser.add_argument(
        '--csv',
        dest='csv_file',
        required=True,
        help="File name with list of students in .csv format."
             "Fields must be delimited by ':', and strings in \"\"."
        )

    parser.add_argument(
        '--teachers',
        dest='teachers',
        required=True,
        help="List of teachers coma delimited"
        )

    parser.add_argument(
            '--passwords',
            dest='passw_file',
            default="",
            required=False,
            help="File where passwords are stored"
            )

    parser.add_argument(
            '--comment',
            dest='comment',
            required=False,
            default="",
            help="Special comment string which describes group of students"
            )

    args = parser.parse_args(arguments_list[1:])

    if os.geteuid() != 0:
        print("You need root permissions to execute this script")
        return 1

    if args.passw_file == "":
        args.passw_file = "paswords_" + args.csv_file

    passw_file = open(args.passw_file, "w")
    os.chmod(args.passw_file, 0o600)
    os.chown(args.passw_file, os.getuid(), os.getgid())

    tmp_file_name = "/tmp/make_students_%d" % os.getpid()

    tmp_passwd_file = open(tmp_file_name, "w")
    os.chmod(tmp_file_name, 0o600)
    #
    # Folowing code has no effect.
    #
    # os.chown(tmp_file_name, os.getuid(), os.getgid())

    hash_salt_file = open("/dev/random", "r")
    hash_salt = hash_salt_file.read(60)
    hash_salt_file.close()

    new_str = ""
    for i in range(0, 60):
        new_str += chr(ord(hash_salt[i]) % (60-30) + 31)

    my_hash = hashlib.sha1()
    today = date.today()
    hash_salt = today.ctime()+new_str
    my_hash.update(hash_salt)

    teachers = args.teachers.split(',')

    for students in parse_csv(args.csv_file):
        full_name = students["name"]
        email = students["email"]
        login = students["username"]

        my_hash.update(login + full_name)
        password = my_hash.hexdigest()[0:12]
        passw_file.write("\"%s\":\"%s\":\"%s\"\n" % (full_name, login, password))
        tmp_passwd_file.write("%s:%s\n" % (login, password))

        command_line = "/usr/sbin/useradd --user-group"\
                       " --comment \"%s,,,%s; %s\" --create-home --shell /bin/bash %s" %\
                       (
                        full_name,
                        email,
                        args.comment,
                        login
                       )
        os.system(command_line)
        #   os.system("echo passwd -e %s" % (login))
        os.system("chmod -R o-rwx ~%s" % login)

        for teacher in teachers:
            os.system("/usr/sbin/usermod -a -G %s %s" % (login, teacher))

        print("User: %s \"%s\" created\n" % (login, full_name))

    tmp_passwd_file.close()
    print("Changing passwords")
    os.system("chpasswd < %s" % tmp_file_name)
    os.unlink(tmp_file_name)

    passw_file.close()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
