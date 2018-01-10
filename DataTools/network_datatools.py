import pandas as pd


def findnetworknodes(network):
    """

    :param network:
    :return:
    """
    return list(pd.unique(network[['Source', 'Target']].values.ravel('K')))


def findaliases(entitylist):
    """

    :param entitylist:
    :return:
    """
    return (entitylist[['Name', 'Alias']].apply(lambda x: ';'.join(x), axis=1)).tolist()
