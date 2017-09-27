#!/bin/env python

import json
from utils import dict_manip as dm
from datetime import datetime


def found_champ_file():
    """ checks for valid league file and returns t/f """
    try:
        with open('data/champ_data.json') as f:
            _ = json.load(f)
    except:
        return False

    return True

def get_champ_id(champ):
    """
    note:
    must use get_riot_champ_name to pass `champ`
    if the name formatting is in question.
    i.e. vel'koz is formatted to velkoz and lee sin is leesin in riot's eyes.
    """
    with open('data/champ_data.json') as f:
        champ_dict = json.load(f)

    return champ_dict['data'][champ]['id']

def get_fancy_champ_name(champ):
    with open('data/champ_data.json') as f:
        champ_dict = json.load(f)

    return champ_dict['data'][champ]['name']

def get_riot_champ_name(champ):
    with open('data/champ_data.json', 'r') as f:
        champ_dict = json.load(f)

    if champ in champ_dict['data']:
        return champ_dict['data'][champ]['name']

    return dm.get_closest(champ_dict['data'], champ)

def get_champ_title(champ):
    with open('data/champ_data.json', 'r') as f:
        champ_dict = json.load(f)

    return champ_dict['data'][champ]['title']

def get_summoner_icon(summoner, region):
    return f'https://avatar.leagueoflegends.com/{region}/{summoner}.png'

def get_summoner_id(summoner_name):
    pass
