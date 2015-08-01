#!/usr/bin/python
# -*- coding: utf-8 -*-
import tweepy
import config as conf

""" Used to take last weeks data, make a graph,
    and the post it to twitter 
"""

# Add credentials to config.example.py and rename to config.py
auth = tweepy.OAuthHandler(conf.consumer_key, conf.consumer_secret)
auth.set_access_token(conf.access_token, conf.access_token_secret)
api = tweepy.API(auth)

from crunch import crunch_data
crunched_data, week, year = crunch_data()

data = {}
for index, row in crunched_data.iterrows():
    data[index] = {#'color': plt.cm.get_cmap('spring')(row.values[0]), 
                   'color': '#000000',
                   'percent': int(row.values[0]*100),
                   'deviation': abs(50 - int(row.values[0]*100))}

from circlegraph import make_figure
filename = make_figure(data, week=week, year=year, font="Latin Modern Mono")

twitter_handles = {'dn.se': '@Dagensnyheter', 'expressen.se': '@Expressen',
                   'svd.se': '@SvD', 'etc.se': '@ETC_redaktionen',
                   'svt.se': '@SVT', 'aftonbladet.se': '@Aftonbladet'}

# Get best and worst
best = sorted(data.iteritems(), key=lambda e: e[1]['deviation'])[0][0]
best_percent = sorted(data.iteritems(), key=lambda e: e[1]['deviation'])[0][1]['percent']
worst = sorted(data.iteritems(), key=lambda e: e[1]['deviation'])[-1][0]
worst_percent = sorted(data.iteritems(), key=lambda e: e[1]['deviation'])[-1][1]['percent']

tweet_to_worst = 'Vecka {week} hade {worst} {worst_percent} % kvinnor i sina texter och var därmed sämst denna vecka. Bäst var {best} med {best_percent} %.'.format(week=week, worst=twitter_handles[worst], worst_percent=worst_percent, best=twitter_handles[best], best_percent=best_percent)
print tweet_to_worst
assert len(tweet_to_worst) < 140

tweet_to_best = 'Vecka {week} hade {best} {best_percent} % kvinnor i sina texter och var därmed bäst denna vecka. Sämst var {worst} med {worst_percent} %.'.format(week=week, worst=twitter_handles[worst], worst_percent=worst_percent, best=twitter_handles[best], best_percent=best_percent)
print tweet_to_best
assert len(tweet_to_worst) < 140

api.update_with_media(filename, status=tweet_to_worst) 
api.update_with_media(filename, status=tweet_to_best) 



