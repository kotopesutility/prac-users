#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
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
    options = dict()

    #
    # set default options
    #
    options['remote_user'] = getpass.getuser()
    options['students_logins'] = "/etc/students.csv"
    options['repository_way'] = "/home/%STUDENT_LOGIN%/repos"

    file_options = open(config_file)
    for record in file_options:
        record = record.strip()
        if record != "" and record[0] == '#':
            continue
        opt = record.split('=')
        if len(opt) == 2:
            options[opt[0].strip()] = opt[1].strip(' \n')

    file_options.close()

    return options


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
                        choices=['clone', 'pull', 'push', 'add-to-trac', 'remove-from-trac'],
                        required=False,
                        default="pull",
                        help="Action with git repository"
                        )

    args = parser.parse_args(arguments_list[1:])

    options = parse_opts(args.config_file)
    print(options)

    if args.action == "clone":
        if not os.path.exists("src"):
            os.mkdir("src")

    for student in parse_csv(options["students_logins"]):
        name  = student["name"]
        login = student["username"]
        local_path = student.setdefault("repo_path", "")

        command_line = ""

        print("begin work for  \"(%s) %s\" ---->" % (name, login))

        if args.action == "clone":
            remote_path = options["repository_way"].replace("%STUDENT_LOGIN%", login)
            command_line = "git clone ssh://%s\@%s%s src/%s %s" %\
                           (
                              options["remote_user"],
                              options["host"],
                              remote_path,
                              login,
                              local_path
                           )

        if args.action == "pull" or args.action == "push":
            command_line = "cd src/%s; git %s; cd .." % (login, args.action)

        if args.action == "add-to-trac":
            command_line = "trac-admin %s repository add %s-%s %s/src/%s/.git git" %\
                            (
                             options["trac_env_path"],
                             options["group_prefix"],
                             login,
                             os.getcwd(),
                             login
                            )

        if args.action == "remove-from-trac":
            command_line = "trac-admin %s repository remove %s-%s" %\
                    (
                            options["trac_env_path"],
                            options["group_prefix"],
                            login
                    )

        os.system(command_line)
        print("finish work for \"%s\" <----\n\n" % login)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
