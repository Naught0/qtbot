#!/bin/env python

import json
from pathlib import Path


def found_user_file():
    """ Checks for user file and returns T/F """
    return Path('data/user_data.json').is_file()

def get_user_info(member, key):
    """ Finds user and prints value of key """
    with open('data/user_data.json', 'r') as user_file:
        user_data = json.load(user_file)

    if (member in user_data) and (key in user_data[member]):
        return user_data[member][key]
    else:
        return None

def create_user(member, key, info):
    """ Creates a user with given info """
    with open('data/user_data.json') as f:
        user_data = json.load(f)

    user_data[member] = {
        key: info
    }

    # Write the new data
    with open('data/user_data.json', 'w') as f:
        json.dump(user_data, f)

def update_user_info(member, key, info):
    """ Updates a user's information """
    with open('data/user_data.json') as f:
        user_data = json.load(f)

    if member in user_data:
        user_data[member][key] = info
        with open('data/user_data.json', 'w') as user_file:
            json.dump(user_data, user_file)

    # User not found
    else:
        create_user(member, key, info)

# Creates user file based on input
def create_user_file(member, key, info):
    """ Creates a user file with given user information """
    new_user = {
        member:
        {
            key: info
        }
    }
    with open('data/user_data.json'):
        json.dump(new_user, f)
