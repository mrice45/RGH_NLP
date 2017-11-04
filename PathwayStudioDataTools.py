"""
This Module is for use in importing networks from Pathway Studio,
as well as exporting networks to other consumers
"""

import re
import pandas as pd


def ps_read_csv(filename):
    raw_data = pd.read_csv(filename, encoding='utf-8')
    return raw_data

def ps_clean_csv(raw_data):


def ps_clean_ref(ref):
    clean = []
    for i in range(len(ref)):
        clean.append((ps_clean_sentence(ref['Ref'][i])))

    ref['Clean_Rf'] = clean
    return ref


def ps_clean_sentence(s):
    s = ps_clear_end(s)
    s = ps_replace_syntax(s)
    return (s)


def ps_clear_end(s):
    clean = re.sub('(?<=\.)[\s\S]+', '', s)
    return clean


def ps_replace_syntax(s):
    clean = re.sub('(ID{.*?})', ps_find_subject, s)
    return clean


def ps_find_subject(s):
    plhldr = s.group(0)
    matchobj = re.search('(?<=\=).*?(?=})', plhldr)
    return matchobj.group(0)