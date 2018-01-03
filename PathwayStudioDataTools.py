"""
This Module is for use in importing networks from Pathway Studio,
as well as exporting networks to other consumers
"""

import re
import pandas as pd


def ps_read_csv(filename):
    """
    Read CSV, and make sure encoding is UTF-16
    :param filename: File to be read
    :return: Raw pandas DataFrame
    """
    raw_data = pd.read_csv(filename, encoding='UTF-16')
    return raw_data

# def ps_clean_csv(raw_data):


def ps_clean_ref(network):
    """
    Take in network, clean references column of PS tags
    :param network: network to have references cleaned from
    :return: Network, with new Clean_References column.
    """
    clean = []
    for i in range(len(network)):
        clean.append((ps_reformat_sentence(network['msrc'][i])))

    network['Clean_References'] = clean
    return network


def ps_reformat_sentence(s):
    """

    :param s:
    :return:
    """
    s = ps_clear_end(s)
    s = ps_replace_syntax(s)
    return s


def ps_clear_end(s):
    """

    :param s:
    :return:
    """
    clean = re.sub('(?<=\.)[\s\S]+', '', s)
    return clean


def ps_replace_syntax(s):
    '''
    Takes in sentence s and removes PS internal formatting
    :param s: Sentence to be formatted
    :return: cleaned sentence.
    '''
    clean = re.sub('(ID{.*?})', __ps_find_subject, s)
    return clean


def __ps_find_subject(s):
    '''PS Internal formatting of subject to just plain-text'''
    plhldr = s.group(0)
    matchobj = re.search('(?<=\=).*?(?=})', plhldr)
    return matchobj.group(0)


def ps_write_csv(network, csv_name='network_please_rename.csv'):
    '''
    Write network, formatted to CSV

    Args:
        network = network to be written to csv.
        sav_name = Name for new file, defaulted 'network_please_rename.csv'
    '''
    network.to_csv(csv_name, encoding="UTF-16")
