#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlalchemy as sq
import pandas as pd
import numpy as np
import datetime

""" Gets data from snapshots.sqlite, and returns last week """

def crunch_data():
    engine = sq.create_engine("sqlite:///snapshots.sqlite")
    df = pd.read_sql_table("snapshots", engine)
    df = df.set_index(['datetime'])

    today = datetime.date.today()
    from_date = today - datetime.timedelta(weeks=1)
    #to_date = today - datetime.timedelta(weeks=1)
    to_date = today

    dframes = []
    for source, df in df.groupby(['source']):
        ts = df.loc[:, 'percent_women']
        ts = ts[ts > 0.0]
        rs = ts.resample("W", how={'median' : np.median})
        rs['week'] = rs.index.weekofyear
        rs = rs[from_date:to_date]
        rs.columns = [source, 'week']
        year = rs.index.year[0]
        week = rs.index.weekofyear[0]
        rs = rs.set_index('week')
        dframes.append(rs)

    df = pd.concat(dframes, axis=1, join='inner')

    return df.T, week, year