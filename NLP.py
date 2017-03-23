import numpy
import nltk
import re
import pandas as pd

'''
Read in file. Currently this is only coming from Pathway Studio, so all of the manipulation is derived from that
formatting. So the following tools take that into consideration. This will one day be updated to take in other sources.
'''

fileOfInterest = input("Enter File Name:")
print(fileOfInterest+" being opened.")

inputFile = pd.read_csv(fileOfInterest);
print(len(inputFile.index))

#Create DataFrame which will be used to manipulate data.
df = pd.DataFrame(columns=['Source', 'Target', 'Data'])

#Clean data so that it fits the DataFrame convention. Also remove duplicated edges.
print("Reading the edges and cleaning data.")
for i in inputFile.index:
    strLine = inputFile.iloc[i][0]
    m = re.search('(?<=: ).*', strLine)
    strLine = m.group()
    m = re.search('.*(?= --)', strLine)
    df_source = m.group()
    m = re.search('(?<=[>|] ).*', strLine)
    df_target = m.group()
    df_data = inputFile.iloc[i][1]

    df.loc[i] = [df_source, df_target, df_data]
    print(inputFile.iloc[i][1])

dp = df.groupby(['Source', 'Target'])['Data'].apply(' '.join).reset_index()
print("Data Table created: Sentences combined")
print(dp)
print("Printing Data cleaned:")
for idx, row in dp.iterrows():
    strLine = row.Data
    strLine = re.sub('\|',' ',strLine)
    strLine = re.sub('\"', '', strLine)
    strLine = re.sub('  ', ' ', strLine)
    row.Data = strLine
    #print(row.Data)

print(dp)


#for accessing ith row:
#input.iloc[i]

#for accessing column named X
#input.X

#for accessing ith row and column named X
#input.iloc[i].X
