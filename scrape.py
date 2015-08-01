#!/usr/bin/python
# -*- coding: utf-8 -*- 

import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
import requests
import re
import warnings
import urllib2
import httplib
from socket import error as SocketError
from progressbar import ProgressBar, ETA, AnimatedMarker
import dataset
import datetime
import time
from random import shuffle

""" Run this to scrape all sites for names and store 
    them in snapshots.sqlite
"""

# TODO:
#   - Fetch names with ÅÄÖåäö
#   - Make multithreaded
#   - Add following news papers: DI, GP, Sydsvenskan, HD

class NameStats():
    """ Class holding all the statistics for gender distribution 
        over names in Sweden """

    def __init__(self, menfile='data/sverige-maen.txt', womenfile='data/sverige-kvinnor.txt'):
        
        men = pd.read_csv(menfile, sep='\t', header=None)
        men.columns = ['gender', 'x', 'y', 'z', 'men', 'name']
        men = men[['name', 'men']]

        women = pd.read_csv(womenfile, sep='\t', header=None)
        women.columns = ['gender', 'x', 'y', 'z', 'women', 'name']
        women = women[['name', 'women']]

        df = pd.concat([women, men])        
        df["name"] = df["name"].map(lambda x: x 
                                    if type(x) != str 
                                    else x.lower())
        df = df.groupby(['name'], as_index=True).sum()
        df = df.fillna(0)
        self.data = df
        
    def gender(self, name, confidence=0.95):
        """ Return gender and confidence """
        try:
            name = name.lower()
            n_men = self.data.loc[name]['men']
            n_women = self.data.loc[name]['women']

            p_men = n_men/(n_men + n_women) 
            p_women = n_women/(n_men + n_women) 

            if p_men > confidence:
                return "man", p_men
            elif p_women > confidence:
                return "woman", p_women
            else:
                return None, (p_men, p_women)
        except KeyError:
            return None, 0



def get_links(url, restrict_to, deeper=True):
    """ Get all links from a webpage """

    try:
        html = urllib2.urlopen(url).read()
        soup = BeautifulSoup(html)
        
        links = set()
        for a in soup.find_all('a', href=True):
            try:
                if ((a['href'][0] == "/" 
                     or restrict_to in a['href']) 
                    and len(a['href']) > 5
                    and "mailto:" not in a['href']):

                    if a['href'][0] == "/":
                        links.update(["http://" + restrict_to + a['href']])
                    else:
                        links.update([a['href']])
            except Exception:
                pass
       
        if deeper:
            next_depth_links = set()
            pbar = ProgressBar(term_width=60)

            i = 0
            for link in pbar(links):
                i += 1
                next_depth_links.update(get_links(link, 
                                                  restrict_to=restrict_to, 
                                                  deeper=False))
                #if i > 0:
                #    break
            
            links.update(next_depth_links)
           
        return list(links)

    except (urllib2.HTTPError, urllib2.URLError, SocketError, UnicodeEncodeError, ValueError):
        print "Error while trying to connect to site"
        return []

### Here goes some functions to handle the specifics 
### to scrape the different news sites

def DN(soup=None):
    if not soup:
        return ("http://dn.se", "dn.se")
 
    text = ""
    for article in soup.find_all('article'):
        text += " " + article.text

    return text

def ETC(soup=None):
    if not soup:
        return ("http://etc.se", "etc.se")

    text = ""
    for article in soup.find_all("div", class_="field field-name-mkts-body-preamble-free"):
        text += " " + article.text

    return text

def SVD(soup=None):
    if not soup:
        return ("http://svd.se", "svd.se")

    text = ""
    for article in soup.find_all("div", class_="Body"):
        text += " " + article.text

    return text

def Arena(soup=None):
    if not soup:
        return ("http://www.dagensarena.se", "dagensarena.se")

    text = ""
    for article in soup.find_all("div", class_="article-content"):
        text += " " + article.text

    return text

def Arbetaren(soup=None):
    if not soup:
        return ("http://arbetaren.se", "arbetaren.se")

    text = ""
    for article in soup.find_all("article", class_="text_sec"):
        text += " " + article.text

    return text

def Flamman(soup=None):
    if not soup:
        return ("http://flamman.se", "flamman.se")

    text = ""
    for article in soup.find_all("div", class_="node-content"):
        text += " " + article.text

    return text

def SVT(soup=None):
    if not soup:
        return ("http://svt.se", "svt.se")

    text = ""
    for article in soup.find_all("div", class_="svtTextBread-Article"):
        text += " " + article.text

    return text

def Aftonbladet(soup=None):
    if not soup:
        return ("http://aftonbladet.se", "aftonbladet.se")

    text = ""
    for article in soup.find_all("div", class_="abBodyText"):
        text += " " + article.text

    return text

def Expressen(soup=None):
    if not soup:
        return ("http://expressen.se", "expressen.se")

    text = ""
    for article in soup.find_all("div", class_="b-text"):
        text += " " + article.text

    return text


def find_names(text):
    """ Crappy regexp that tries to find names of the 
        pattern Firstname Lastname.

        TODO: make it handle more than just ascii 
              chars i.e. ÅÄÖ in this Swedish context.
    """
    names = []
    for name in re.findall("(([A-Z])[\w-]*(\s+[A-Z][\w-]*)+)", text):
        names.append(name[0].split()[0])
    return list(set(names))
    
def get_snapshot(article_parser):
    """ Gets a snapshot of all the names for today on a news site """

    url, restrict_to = article_parser() # hacky way to get function metadata

    print "============================================================"
    print "Downloading all links from:", restrict_to
    print "============================================================"
    links = get_links(url, restrict_to=restrict_to)
    print "Found {} links".format(len(links))
    print "Parsing links for names... "

    all_names = []
    pbar = ProgressBar(term_width=60)

    if links:
        for link in pbar(links):
         
            try:
                html = urllib2.urlopen(link, timeout=5).read()
                soup = BeautifulSoup(html)
                text = article_parser(soup)

                names = find_names(text)
                all_names += names

            except (urllib2.HTTPError, 
                    urllib2.URLError,
                    httplib.BadStatusLine,
                    httplib.IncompleteRead,
                    SocketError, 
                    UnicodeEncodeError, 
                    ValueError):
                text = ""

        print "Found {} names".format(len(all_names))

    return all_names

def calc_perc_women(snapshot):
    """ Calculate percent women of a snapshot """

    men, women = 0, 0
    
    for name in snapshot:
        try:
            if ns.gender(name)[0] == "man":
                men += 1
            elif ns.gender(name)[0] == "woman":
                women += 1
        except:
            pass
           
    if men + women != 0:     
        percent = float(women) / float(men + women)
        print 'Found {} % women mentioned \n'.format(int(percent * 100))
        return percent
    else:
        return 0

def crawl_all():
    """ Main function that goes through all sites, 
        crawls them, and then waits a day untill it
        does it again. 
    """
    
    db = dataset.connect('sqlite:///snapshots.sqlite')
    table = db['snapshots']

    while True:
        time1 = time.time()
        to_parse = [Aftonbladet, Expressen, Flamman, ETC, DN, SVT, SVD]
        shuffle(to_parse)

        for parser in to_parse:
            snapshot = get_snapshot(article_parser=parser)
            percent_women = calc_perc_women(snapshot)

            table.insert(dict(percent_women=percent_women, 
                              snapshot=" ".join(snapshot),
                              datetime=datetime.datetime.now(),
                              source=parser()[1],
                              n_names=len(snapshot)))

        # Wait a day since crawling started
        time2 = time.time()
        print "Waiting a day since crawling started..."
        time.sleep(24*60*60-(time2-time1))

#html = urllib2.urlopen("http://www.svd.se/ett-lunchmote-med-harenstam-i-full-blom/om/magnus-harenstam-dod").read()
#soup = BeautifulSoup(html)
#print find_names(SVD(soup))

ns = NameStats()
crawl_all()
#get_snapshot(article_parser=SVD)




