#!/usr/bin/env python3
import merger as mg
import index_conversions as ic
import pandas as pd

# This gives us a number of outputs 
# (see https://pycubelib.readthedocs.io/en/latest/merger.html)
output_i = mg.process_cubex('../test_data/profile.cubex', exclusive=False)


df_i = output_i.df # Dataframes with the metrics

tree = output_i.ctree_df # Dataframe containing info on the calltree

# We convert the Cnode IDs to short callpaths in the dataframe.
df_i = ic.convert_index(
        df_i,
        tree,
        target = 'Short Callpath')

# We calculate the mean of the time
times_mean = df_i.time.groupby('Short Callpath').mean()

# We do a merge (=join) on the tree dataframe to find the parent-child relation 
parent_child = ( pd.merge(left=tree,                     #
                          right=tree,                    #
                          left_on='Cnode ID',            #
                          right_on='Parent Cnode ID',    #
                          suffixes=('-Parent', ''))      #
                 # we select the two columns we're interested in
                 .loc[:, ['Short Callpath', 'Short Callpath-Parent']]  
                 .set_index('Short Callpath'))  # so that we can join eas


def filter_small_time(df,rel_threshold):
    '''
    Removes rows relative to small time function calls.
    '''
    column = df['Time (Inclusive)'] 
    condition = column > column.max() * rel_threshold
    return df.loc[condition,:]

data = ( pd.concat([times_mean,parent_child],      #
                   axis = 'columns')               #
         .reset_index()                            #
         .rename(                                  #
             mapper = {                            #
                 'index':'Short Callpath',         #
                 'time':'Time (Inclusive)',        #
                 'Short Callpath-Parent':'Parent'},#
             axis = 'columns')                     #
         .pipe(filter_small_time,                  #
               rel_threshold=0.01))                #

# PLOTLY 
import plotly.express as px

fig = px.sunburst( data,  #
                   names=data['Short Callpath'],  #
                   parents=data['Parent'],  #
                   values=data['Time (Inclusive)'])  #

# Shows in a browser. 
fig.show() # it can be exported to .png or .jpeg from the browser view
fig.write_html('sunburst.html') # a huge html file is produced


