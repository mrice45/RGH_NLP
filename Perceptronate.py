from DataTools import ps_datatools as psdt
import pandas as pd
import os

filelocation = input('Input file location: ')
max_in = input('Input max number of in_degree: ')
fn = os.path.splitext(filelocation)[0]
df = psdt.ps_perceptronify(filelocation, max_in)
df.to_csv(fn + '_perceptron.csv', index=False)

print('All done perceptronating, check this directory for your file called: ' + fn + '_perceptron.csv')