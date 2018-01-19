"""
This Module is for use in importing networks from Pathway Studio,
as well as exporting networks to other consumers
"""

import re
import pandas as pd
import math


def ps_read_csv(filename, ps_format=True):
    """
    Read CSV from Pathway Studio, with or without initial data clean
    :param filename: File to be read
    :param ps_format: Boolean to format PS raw to cleaned
    :return: Raw pandas DataFrame, or cleaned pandas DF
    """

    rawdata = pd.read_csv(filename)

    if ps_format:
        network = __ps_networkdataframe(rawdata)
        network = ps_clean_ref(network)
        return network

    else:
        return rawdata


def ps_read_entitylist(filename):
    """
    Read the Pathway Studio Entity List file export
    :param filename: path/to/file
    :return: pandas DataFrame of Name and Alias
    """

    entitylist = pd.read_csv(filename)
    return entitylist[['Name', 'Alias']]


def __ps_networkdataframe(rawdata):
    """
    Internal function to format raw PS to formatted DataFrame
    :param rawdata: Raw PS dataframe
    :return: formatted DataFrame
    """

    network = pd.DataFrame(columns=['Source', 'Target', 'Data'])

    for i in rawdata.index:
        # Clean this later with loc[]
        strLine = rawdata.iloc[i]['RelationSymbolicName']
        m = re.search('(?<=: ).*', strLine)
        strLine = m.group()
        m = re.search('.*(?= --)', strLine)
        df_source = m.group()
        m = re.search('(?<=[>|] ).*', strLine)
        df_target = m.group()
        df_data = rawdata.iloc[i]['msrc']
        network.loc[i] = [df_source, df_target, df_data]

    network['RefNo'] = rawdata.RelationNumberOfReferences
    network['PS_Polarity'] = rawdata.Effect
    network['Duplicated'] = False

    return network


def ps_has_duplicates(network):
    """
    Boolean check to see if there are duplicated rows
    :param network:
    :return:
    """
    if network.duplicated(subset=['Source', 'Target']):
        return True
    # This might need a keep=False in the duplicated call


def ps_return_duplicates(network):
    """
    Returns duplicated rows in DF
    :param network:
    :return:
    """
    return network[network.duplicated(subset=['Source', 'Target'], keep=False)] \
        .sort_values(by=['Source', 'Target']).reset_index(drop=True)


def ps_flag_duplicates(network):
    """
    Changes Duplicated bool to True if duplicated.
    :param network:
    :return:
    """

    # Add validation that this is a PS network that's been cleaned
    if 'Duplicated' in network.columns:
        dupes = network[network.duplicated(subset=['Source', 'Target'], keep=False)].index
        network.loc[dupes, 'Duplicated'] = True
        return network
    else:
        raise Exception("Duplicated col not present")


def ps_drop_duplicates(network):
    """
    Drops Duplicates from network
    :param network:
    :return: network df minus the duplicates
    """
    dupes = network[network.duplicated(subset=['Source', 'Target'], keep=False)].index
    network.drop(dupes)
    return network.reset_index()


def ps_clean_ref(network):
    """
    Take in network, clean ALL references column of PS tags
    :param network: network to have references cleaned from
    :return: Network, with new Clean_References column.
    """
    clean = []
    for i in range(len(network)):
        clean.append((ps_clean_sentence_tags(network['msrc'][i])))

    network['Clean_References'] = clean
    return network


def ps_clean_sentence_tags(s):
    """
    Removes PS tags from SINGLE reference.
    :param s:
    :return:
    """
    s = ps_clear_end(s)
    s = ps_replace_syntax(s)
    return s


def ps_clear_end(s):
    """
    Removes trailing whitespace from PS sentences.
    :param s:
    :return:
    """
    clean = re.sub('(?<=\.)[\s\S]+', '', s)
    return clean


def ps_replace_syntax(s):
    """
    Takes in sentence s and removes PS internal formatting
    :param s: Sentence to be formatted
    :return: cleaned sentence.
    """
    clean = re.sub('(ID{.*?})', __ps_find_subject, s)
    return clean


def __ps_find_subject(s):
    """PS Internal formatting of subject to just plain-text"""
    plhldr = s.group(0)
    matchobj = re.search('(?<=\=).*?(?=})', plhldr)
    return matchobj.group(0)


def ps_perceptronify(in_network, max_indegree=8):
    """
    Function to create a perceptron network based on input network from pathway studio. Splits nodes with high
    in-degrees into a sub network of nodes that feed into a perceptron node, thus limiting the number of
    edges coming into any single node.

    :param in_network: File Location of network to perceptronify
    :param max_indegree: Max number of edges node can have coming in.
    :return: Network that has been perceptronified.
    """
    rawnetwork = pd.read_csv(in_network, error_bad_lines=False)

    network = pd.DataFrame(columns=list(rawnetwork.columns))
    network['Source'] = rawnetwork['Source']
    network['Target'] = rawnetwork['Target']
    network['Polarity'] = rawnetwork['Polarity']

    if 'Data' in list(network.columns):
        network['Data'] = rawnetwork['Data']

    g = network.groupby('Target')
    network = g.apply(lambda grp: __splitgroup(grp.reset_index(), 6))

    network.reset_index(drop=True)
    network.sort_values(by=['Target'], inplace=True)
    network.reset_index(inplace=True, drop=True)

    perceptron_base = network.Target.apply(__find_base_target)
    perceptron_base = list(set([item[0] for item in perceptron_base if item]))

    temp = network.loc[network.Source.apply(lambda x: x in perceptron_base)]['Source'].apply(__renamesource)
    network.loc[temp.index, 'Source'] = temp.values

    if network['Data']:
        network = network[['Source', 'Target', 'Polarity', 'Data']]
    else:
        network = network[['Source', 'Target', 'Polarity']]

    return network


def __find_base_target(target):  # RENAME
    return re.findall('.*(?=__Perceptron)', target)


def __renamesource(x):
    x = x + '__Perceptron'
    return x


def __splitgroup(grp, inmax):
    '''
    Internal helper for perceptronify
    :param grp:
    :param inmax:
    :return:
    '''
    name = grp['Target'].iloc[0]
    cols = ['Source', 'Target', 'Polarity']
    lst = []

    if len(grp) > inmax:
        numperceptrons = math.ceil(len(grp) / inmax)
        cnt = 1
        for num in range(len(grp)):
            rename = name + '__' + str(cnt)
            grp['Target'].iloc[num] = rename
            if cnt == numperceptrons:
                cnt = 1
            else:
                cnt = cnt + 1
        for num in range(numperceptrons):
            # lst.append([name+'__'+str(num+1),(name+'__Perceptron'),'NaN','NaN'])
            lst.append([name + '__' + str(num + 1), (name + '__Perceptron'), 'NaN'])
    perceptron = pd.DataFrame(lst, columns=cols)
    df = grp.append(perceptron)
    return df


def ps_write_csv(network, csv_name='network_please_rename.csv', exclude_unknown=False):
    """
    Write network, formatted to CSV

    :param network: network to be written to csv.
    :param csv_name: Name for new file, defaulted 'network_please_rename.csv'
    :param exclude_unknown: flag to exclude rows where Polarity is unknown
    :return: none
    """
    network.to_csv(csv_name, encoding="UTF-16")
    if exclude_unknown:
        network[network['Polarity'] != 'unknown'].reset_index().to_csv(csv_name, encoding="UTF-16")
