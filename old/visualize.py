#!/usr/bin/python
# -*- coding: utf-8 -*- 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import sqlalchemy as sq
import numpy as np
import bootstrap

def moe_binomial(p, n, confidence):
    """ Calculate marigin of error 
        for a binomial distribution """
    
    if confidence == 0.95:
        Z = 1.96 
    elif confidence == 0.99:
        Z = 2.57
    elif confidence == 0.9973:
        Z = 3
    else:
        return None
    
    return Z*np.sqrt((p*(1-p))/n)

def moe(sample, confidence):
    
    if confidence == 0.95:
        Z = 1.96 
    elif confidence == 0.99:
        Z = 2.57
    elif confidence == 0.9973:
        Z = 3
    else:
        return None
    
    std = np.std(sample)
    n = len(sample)
    
    return Z*std/np.sqrt(n)

fig, ax = plt.subplots()

engine = sq.create_engine("sqlite:///snapshots.sqlite")
df = pd.read_sql_table("snapshots", engine)
df = df.set_index(['datetime'])

#df.groupby('source')['percent_women'].plot(ax=ax, legend=True)
#fig.savefig("snapshots.png")

#sample = df[df['source'] == 'dn.se']['percent_women'].values
#print sample
#print "{} ± {}".format(np.mean(sample), moe(sample=sample, confidence=0.95))

#print bootstrap.ci(sample)
#print np.mean(bootstrap.ci(sample)) - bootstrap.ci(sample)[0]

import datetime
today = datetime.date.today()
from_date = today - datetime.timedelta(weeks=5)
to_date = today - datetime.timedelta(weeks=1)

funcs = {'mean' : np.mean}
dframes = []

for source, df in df.groupby(['source']):
    #print source
    ts = df.loc[:, 'percent_women']
    ts = ts[ts > 0.0]
    rs = ts.resample("W", how=funcs)
    rs['week'] = rs.index.weekofyear
    rs = rs[from_date:to_date]
    #rs = rs.reset_index(drop=False)
    rs.columns = [source, 'week']
    rs = rs.set_index('week')
    #print rs
    dframes.append(rs)


df = pd.concat(dframes, axis=1, join='inner')
print df.T


"""
fig, ax = plt.subplots()
result = pd.concat(dframes)
result.groupby('source')['Mean'].plot(ax=ax, legend=True, style='-o')
for line in ax.lines:
    line.set_linewidth(2)
    line.set_markersize(8)
    line.set_markeredgecolor('none')

ax.set_ylim(0,0.5)


fig.savefig("snapshots_week.png")
"""


