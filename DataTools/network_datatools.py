import re
import pandas as pd

def findnetworknodes(network):
     return list(pd.unique(network[['Source', 'Target']].values.ravel('K')))

