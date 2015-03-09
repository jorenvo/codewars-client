#!/usr/bin/env python3
# Copyright 2014 Joren Van Onder
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib.request
import urllib.parse
import urllib.error
import sys
import json
import pprint
import argparse

def parseArguments():
    parser = argparse.ArgumentParser(description = "Provides users with a way of using codewars.com without having to use a browser to do their programming in.")
    parser.add_argument("-d", "--description-file", help = "file containing the description (default: %(default)s)", default = "description.html")
    parser.add_argument("-s", "--solution-file", help = "file containing the solution (default: %(default)s)", default = "solution.js")
    parser.add_argument("-t", "--tests-file", help = "file containing the tests (default: %(default)s)", default = "tests.js")
    parser.add_argument("-k", "--api-key-file", help = "file containing codewars.com api key (default: %(default)s)", default = "api_key.txt")
    parser.add_argument("action", choices = ["next", "submit"], help = "next: setup the next kata, submit: attempt solution")
    args = parser.parse_args()

    return(args)

def readFile(name):
    f = open(name, 'r')
    contents = f.read()
    f.close()

    return(contents)

def writeStringToFile(filename, string):
    f = open(filename, 'w')
    print(string, end="", file=f)
    f.close()

def prettyPrint(obj):
    pp = pprint.PrettyPrinter(indent = 4)
    pp.pprint(obj)

def doPost(url, headers, data):
    data = urllib.parse.urlencode(values)
    data = data.encode("utf-8")

    req = urllib.request.Request(url, data, headers)

    try:
        response = urllib.request.urlopen(req).read().decode("utf-8")
    except urllib.error.HTTPError as err:
        print("*code*\n" + str(err.code) + "\n*reason*\n" + str(err.reason) + "\n*headers*\n" + str(err.headers))
        sys.exit(1)

    response = json.loads(response)
    return(response)

def nextKata():
    # response = doPost("https://www.codewars.com/api/v1/code-challenges/javascript/train",
    #                   {'Authorization': apikey},
    #                   {'peek': 'false'});

    response = open('test.json', 'r').read()
    jsonified = json.loads(response)

    writeStringToFile(arguments.description_file, jsonified["description"])
    writeStringToFile(arguments.tests_file, jsonified["session"]["exampleFixture"])
    writeStringToFile(arguments.solution_file, jsonified["session"]["setup"])
    writeStringToFile(".current_challenge_ids", jsonified["session"]["projectId"] + "\n" + jsonified["session"]["solutionId"])

    print("Set up kata \"" + jsonified["name"] + "\"")

arguments = parseArguments()
apikey = readFile(arguments.api_key_file)

if arguments.action == "next":
    nextKata()
elif arguments.action == "submit":
    print("def")
# response = urllib.request.urlopen("https://www.codewars.com/api/v1/code-challenges/5277c8a221e209d3f6000b56").read().decode("utf-8")
# jsonified = json.loads(response)
# prettyPrint(jsonified)

# 1. start next challenge (description: description.html) (project_id + solution_id: current_challenge_id.txt) (./codewars.py next)
# 2. write code (solution.js)
# 3. submit answer (+ poll) (needs challenge id) (./codewars.py submit solution.js)
