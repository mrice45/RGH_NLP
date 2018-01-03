import re
import pandas as pd
import sentiment_analysis


"""network_csv = pd.read_csv(input('Enter Filename:'))  #Read in file,error checking will come later. 
For now, I trust me."""
network_csv = pd.read_csv('RIG-I reduced.csv', encoding='UTF-16')
network_csv

"""Conform Data"""
network = pd.DataFrame(columns=['Source', 'Target', 'Data'])

for i in network_csv.index:
    strLine = network_csv.iloc[i]['RelationSymbolicName']
    m = re.search('(?<=: ).*', strLine)
    strLine = m.group()
    m = re.search('.*(?= --)', strLine)
    df_source = m.group()
    m = re.search('(?<=[>|] ).*', strLine)
    df_target = m.group()
    df_data = network_csv.iloc[i]['msrc']

    network.loc[i] = [df_source, df_target, df_data]

network['RefNo'] = network_csv.RelationNumberOfReferences
network['PS_Polarity'] = network_csv.Effect
network['Duplicated'] = False
network2 = network

dict_tag = sentiment_analysis.DictionaryTagger(['postive.yml', 'negative.yml', 'inv.yml'])

"""Sentiment Scoring, possibly add weight to individual words [promote, inhibit]"""
score = []
for chunk in network['Data']:
    split_sentences = sentiment_analysis.split(chunk)
    pos_sentences = sentiment_analysis.pos_tag(split_sentences)
    tagged_sentences = dict_tag.tag(pos_sentences)
    relationship_score = sentiment_analysis.sentiment_score(tagged_sentences)
    
    score.append(relationship_score)


network['Sentiment Score'] = score
polarity = []
for sc in score:
    if sc > 0:
        polarity.append('positive')
    elif sc < 0:
        polarity.append('negative')
    else:
        polarity.append('unknown')

network['Polarity'] = polarity
network.loc[network['Polarity'] != network['PS_Polarity'], 'Polarity_Changed'] = True
network.loc[network['Polarity'] == network['PS_Polarity'], 'Polarity_Changed'] = False

network.to_csv('RIG-I reduced_SA.csv', encoding="UTF-16")

network[network['Polarity'] != 'Unknown'].reset_index().drop('Data',1).to_csv(path_or_buf='HPG_HPA_Sentiment.csv',
                                                                              columns= ['Source','Target', 'Polarity'],
                                                                              index=False)

network[network.duplicated(subset=['Source','Target'], keep=False)].sort_values(by=['Source', 'Target'])



