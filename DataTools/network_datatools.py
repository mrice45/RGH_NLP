import re
import pandas as pd


def findnetworknodes(network):
    return list(pd.unique(network[['Source', 'Target']].values.ravel('K')))


def findaliases(entitylist):
    return entitylist[['Name', 'Alias']].apply(lambda x: ';'.join(x), axis=1)
