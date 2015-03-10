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
from time import sleep

challengeIdsFileName = ".current_challenge_ids"

def parseArguments():
    parser = argparse.ArgumentParser(description = "Provides users with a way of using codewars.com without having to use a browser to do their programming in.")
    parser.add_argument("-d", "--description-file", help = "file containing the description (default: %(default)s)", default = "description.html")
    parser.add_argument("-s", "--solution-file", help = "file containing the solution (default: %(default)s)", default = "solution.js")
    parser.add_argument("-t", "--tests-file", help = "file containing the tests (default: %(default)s)", default = "tests.js")
    parser.add_argument("-k", "--api-key-file", help = "file containing codewars.com api key (default: %(default)s)", default = "api_key.txt")
    parser.add_argument("-e", "--evaluation-file", help = "file containing the response after submitting (default: %(default)s)", default = "evaluation.html")
    parser.add_argument("action", choices = ["next", "submit", "finalize"], help = "next: setup the next kata, submit: attempt solution, finalize: finalize last submitted solution")
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

def readChallengeIds():
    contents = readFile(challengeIdsFileName).split("\n")

    return({"projectId": contents[0],
            "solutionId": contents[1]})

def prettyPrint(obj):
    pp = pprint.PrettyPrinter(indent = 4)
    pp.pprint(obj)

def doPost(url, data = {}):
    data = urllib.parse.urlencode(data)
    data = data.encode("utf-8")
    headers = {'Authorization': apikey}

    req = urllib.request.Request(url, data, headers)

    try:
        response = urllib.request.urlopen(req).read().decode("utf-8")
    except urllib.error.HTTPError as err:
        print("*code*\n" + str(err.code) + "\n*reason*\n" + str(err.reason) + "\n*headers*\n" + str(err.headers))
        sys.exit(1)

    response = json.loads(response)
    return(response)

# This prepends some preamble and converts the codewars' tests to
# mocha compatible tests that use nodejs' Assert
# http://www.codewars.com/docs/js-slash-coffeescript-test-reference
# https://nodejs.org/api/assert.html#assert_assert_equal_actual_expected_message
def makeTestsCompatibleWithMocha(tests):
    # var assert = require("assert");
    # var exported = require("./solution.js");
    tests = "\
var assert = require(\"assert\");\n\
var kata = require(\"./" + arguments.solution_file + "\");\n\n" + tests

    tests = tests.replace("Test.assertEquals", "assert.strictEqual")
    tests = tests.replace("Test.assertNotEquals", "assert.notStrictEqual")
    tests = tests.replace("Test.assertNotEquals", "assert.notStrictEqual")
    tests = tests.replace("Test.assertSimilar", "assert.equal") # not really the same. Test.assertSimilar does toString and then ===
    tests = tests.replace("Test.assertNotSimilar", "assert.notEqual")
    tests = tests.replace("Test.expectError", "assert.throws") # not perfect either because assert.throws expects (block[, error][, message])
    tests = tests.replace("Test.expectNoError", "assert.doesNotThrow")

    return(tests)

def nextKata():
    response = doPost("https://www.codewars.com/api/v1/code-challenges/javascript/train");

    ## TEST START ##
    # response = open('test.json', 'r').read()
    # response = json.loads(response)
    ## TEST END ##

    writeStringToFile(arguments.description_file, response["description"])
    writeStringToFile(arguments.solution_file, response["session"]["setup"])
    writeStringToFile(challengeIdsFileName, response["session"]["projectId"] + "\n" + response["session"]["solutionId"])

    mochaTests = makeTestsCompatibleWithMocha(response["session"]["exampleFixture"])
    writeStringToFile(arguments.tests_file, mochaTests)

    print("Set up kata \"" + response["name"] + "\"")

def pollForResponse(dmid):
    response = None

    while True:
        response = urllib.request.urlopen("https://www.codewars.com/api/v1/deferred/" + dmid).read().decode("utf-8")
        response = json.loads(response)

        try:
            if response["success"]:
                break
        # while codewars is evaluating the solution the json will not contain success at all
        except KeyError:
            pass

        sleep(2)

    writeStringToFile(arguments.evaluation_file, response["output"][0])

    print("Solution was evaluated and ", end="")

    if response["valid"]:
        print("passed.")
    else:
        print("failed with reason:\n" + response["reason"])

    print("Summary: " + str(response["summary"]["errors"]) + " errors, " + str(response["summary"]["failed"]) + " failed, " + str(response["summary"]["passed"]) + " passed")

    print("Additional output was written to " + arguments.evaluation_file + ".")

def submitKata():
    challengeIds = readChallengeIds()
    prettyPrint(challengeIds)

    response = doPost("https://www.codewars.com/api/v1/code-challenges/projects/" + challengeIds["projectId"] + "/solutions/" + challengeIds["solutionId"] + "/attempt",
                      {"code": readFile(arguments.solution_file)})
    prettyPrint(response)

    pollForResponse(response["dmid"])

arguments = parseArguments()
apikey = readFile(arguments.api_key_file)

if arguments.action == "next":
    nextKata()
elif arguments.action == "submit":
    submitKata()
elif arguments.action == "finalize":
    finalizeKata()

# response = urllib.request.urlopen("https://www.codewars.com/api/v1/code-challenges/5277c8a221e209d3f6000b56").read().decode("utf-8")
# jsonified = json.loads(response)
# prettyPrint(jsonified)

# 1. start next challenge (description: description.html) (project_id + solution_id: current_challenge_id.txt) (./codewars.py next)
# 2. write code (solution.js)
# 3. submit answer (+ poll) (needs challenge id) (./codewars.py submit solution.js)
