import pandas as pd


def findnetworknodes(network):
    """
    Take a network with columns 'Source' and 'Target',
    Return unique nodes in said network
    :param network:
    :return: list of unique nodes
    """
    return list(pd.unique(network[['Source', 'Target']].values.ravel('K')))


def findaliases(entitylist):
    """
        Take in a dataframe that has nodes and their aliases, return a list that joins the Aliases
    :param entitylist:
    :return: List of [Name, Alias]
    """
    return (entitylist[['Name', 'Alias']].apply(lambda x: ';'.join(x), axis=1)).tolist()
