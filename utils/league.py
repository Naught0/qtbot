#!/bin/env python

import json

from utils import dict_manip as dm


def get_champ_id(champ_data: dict, champ: str):
    """
    note:
    must use get_riot_champ_name to pass `champ`
    if the name formatting is in question.
    i.e. vel'koz is formatted to velkoz and lee sin is leesin in riot's eyes.
    """
    return champ_data['data'][champ]['id']


def get_fancy_champ_name(champ_data: dict, champ: str):
    return champ_data['data'][champ]['name']


def get_riot_champ_name(champ_data: dict, champ: str):
    if champ in champ_data['data']:
        return champ

    return dm.get_closest(champ_data['data'], champ)


def get_champ_title(champ_data: dict, champ: str):
    return champ_data['data'][champ]['title']


def get_summoner_icon(summoner: str, region: str = 'na'):
    return f'https://avatar.leagueoflegends.com/{region}/{summoner}.png'


def get_summoner_id(summoner_name):
    pass
