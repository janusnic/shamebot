#!/usr/bin/python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches            
from matplotlib.lines import Line2D   
import operator 

""" Used to make donut charts """

def colorscale(hexstr, scalefactor):
    """ Used to take a hex color and make it
        lighter or darker. Found on Stack Overflow
        don't remeber author. Sorry. """

    def clamp(val, minimum=0, maximum=255):
        if val < minimum:
            return minimum
        if val > maximum:
            return maximum
        return val
    
    hexstr = hexstr.strip('#')

    if scalefactor < 0 or len(hexstr) != 6:
        return hexstr

    r, g, b = int(hexstr[:2], 16), int(hexstr[2:4], 16), int(hexstr[4:], 16)

    r = clamp(r * scalefactor)
    g = clamp(g * scalefactor)
    b = clamp(b * scalefactor)

    return "#%02x%02x%02x" % (r, g, b)

def luminocity(hexstr):
    """ Calculate luminocity from hex color """

    hexstr = hexstr.strip('#')
    r, g, b = int(hexstr[:2], 16), int(hexstr[2:4], 16), int(hexstr[4:], 16)
    
    return 0.2126*r + 0.7152*g + 0.0722*b

def make_figure(the_data, week, year, font="Latin Modern Mono"):
    """ Makes a donut chart """
    
    fig, ax = plt.subplots(dpi=300, figsize=(10,10))
    ax.axis('equal')

    width = 0.13
    circlekwargs = dict(startangle=90, wedgeprops = {'linewidth': 1})
    props = dict(boxstyle='round', facecolor='white', edgecolor='none', alpha=0.0)
    textkwargs = dict(fontsize=14, verticalalignment='top', horizontalalignment='right', 
                      bbox=props, family=font, color="black")

    rings = []

    for i, (source, data) in enumerate(sorted(the_data.iteritems(), 
                                              key=lambda e: e[1]['percent'], 
                                              reverse=True)):
        color = data['color']
        percent = data['percent']
        percents = [100-percent, percent]
        
        ring, _ = ax.pie(percents, 
                         radius=1-width*i, 
                         colors=["#ffffff", color], 
                         **circlekwargs)
        
        ax.text(0.427, 1-width*i*0.40-0.118, u'{}'.format(source), transform=ax.transAxes, **textkwargs)
        
        ax.text(0.484, 1-width*i*0.40-0.118, u'{}%'.format(percent), transform=ax.transAxes, weight="bold", **textkwargs)
        
        rings += ring

    plt.setp(rings, width=width, edgecolor='white')

    plt.title(u'Procent omnämnda kvinnor (med namn)',
             family=font, fontsize=28,
            weight="bold")
    plt.xlabel("vecka {}, {}".format(week, year),
              family=font, fontsize=18,
            weight="bold") 
                                          
    l = Line2D([0,0],[-1,0], linestyle='--', color="black", linewidth=1)                                    
    ax.add_line(l)     

    filename = "graphs/data.png"
    plt.savefig(filename)

    return filename

