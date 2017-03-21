import numpy
import nltk
import re
import pandas as pd

fileOfInterest = input("Enter File Name:")
print(fileOfInterest+" being opened.")

inputFile = pd.read_csv(fileOfInterest);
print(len(inputFile.index))
df = pd.DataFrame(columns=['Source', 'Target', 'Data'])

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




#for accessing ith row:
#input.iloc[i]

#for accessing column named X
#input.X

#for accessing ith row and column named X
#input.iloc[i].X
