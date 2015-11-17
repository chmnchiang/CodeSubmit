#! /usr/bin/env python3

from getpass import getpass
import argparse
from robobrowser import RoboBrowser
import requests
import json
import time

def get_submission_data(user):
    req = requests.get('http://codeforces.com/api/user.status?'
                       'handle={}&from=1&count=1'.format(user))
    content = req.content.decode()
    js = json.loads(content)
    if 'status' not in js or js['status'] != 'OK':
        raise ConnectionError('Codeforces BOOM!')
    res = js['result'][0]
    id_, verdict = res['id'], res['verdict']
    return id_, verdict


def main():

    parser = argparse.ArgumentParser(
        description='Submit codeforces in command line')
    parser.add_argument('user', type=str,
                        help='Your codeforces ID')
    parser.add_argument('prob', type=str,
                        help='Codeforces problem ID (Ex: 33C)')
    parser.add_argument('file', type=str,
                        help='path to the source code')
    args = parser.parse_args()

    user_name = args.user
    last_id, _ = get_submission_data(user_name)

    passwd = getpass()

    browser = RoboBrowser()
    browser.open('http://codeforces.com/enter')

    enter_form = browser.get_form('enterForm')
    enter_form['handle'] = user_name
    enter_form['password'] = passwd
    browser.submit_form(enter_form)

    try:
        checks = list(map(lambda x: x.getText()[1:].strip(),
            browser.select('div.caption.titled')))
        if user_name not in checks:
            print("Login Failed.. probably because you've typed"
                  "a wrong password.")
            return
    except Exception as e:
        print("Login Failed.. probably because you've typed"
              "a wrong password.")
        return 

    browser.open('http://codeforces.com/problemset/submit')
    submit_form = browser.get_form(class_='submit-form')
    submit_form['submittedProblemCode'] = args.prob
    submit_form['sourceFile'] = args.file
    browser.submit_form(submit_form)

    if browser.url[-6:] != 'status':
        print('Your submission has failed, probably '
              'because you have submit the same file before.')
        return

    print('Submitted, wait for result...')
    while True:
        id_, verdict = get_submission_data(user_name)
        if id_ != last_id and verdict != 'TESTING':
            print('Verdict = {}'.format(verdict))
            break
        time.sleep(5)

if __name__ == '__main__':
    main()
