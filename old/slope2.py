# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 22:32:04 2013

@author: pascal Schetelat
"""



import matplotlib.pyplot as plt
import pandas as pd



def slope(data,ax=None): 
    """====
Slope
====

Definition: Slope(*args, **kwargs)

----

Plot Slope plot Tufte Style
:class:`~matplotlib.axes.Axes`. 

Parameters
----------
data : pandas dataFrame
    index indicate the categories
    columns indicate time / period
ex :
            before  after
country                  
Argentina       67     74
Bangladesh      54     53
Brazil          62     68
Canada          73     80
China           68     72
    

Examples
--------
>>> d = {'col1': ts1, 'col2': ts2}
>>> df = DataFrame(data=d, index=index)
>>> df2 = DataFrame(np.random.randn(10, 5))
>>> df3 = DataFrame(np.random.randn(10, 5),
    
    """

    df = data.copy()
    ax = df.T.plot(ax=ax,legend = False,grid=False,color='k',alpha=0.5)
    f = ax.get_figure()
    

    cols  = df.columns
    df['__label__'] = df.index

    for i,col in enumerate(cols) :        
        # this step is trivial as the values are integer
        # when messier data will arrive, use pd.cut to tile 
        # by categories dependin gon the number of lines 
        # you want plotted on the graph
        
        if i == 0 : 
            hl = 'right'
        elif i == len(cols)-1:
            hl = 'left'            
        else : 
            hl  = 'center'
        print i, hl    
        labels = df.groupby(col)['__label__'].agg(', '.join)
      
        labs=  labels.reset_index().values
        for lab in labs : 

            ax.text(i, lab[0],lab[1],
                             horizontalalignment=hl)

    ax.set_xbound(-2,len(cols)+1)
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_yticklabels([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_xticks([])
    ax.xaxis.grid(False)
    plt.tight_layout()


    f.savefig('text.pdf')
        
    return ax
    
    
if __name__ == '__main__' : 
    
    data_tv     = pd.read_csv('Data/television.csv',names = ['country','before','after'],index_col=0)

    data_tv
    print data_tv.head()
    ax = slope(data_tv)   
        
    