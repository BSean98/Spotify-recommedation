# -*- coding: utf-8 -*-
"""Spotify.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QkcOgnkelBUNkVIf9dodqphuhJRuzhqs
"""

import pandas as pd
import numpy as np

"""**IMPORTING THE DATA**"""

data = pd.read_csv("/content/drive/MyDrive/data.csv")
data.head(5)

"""**VIEWING THE DIMENSIONS OF THE DATA**"""

print(data.shape)
data.columns

"""**Checking for NULL Values**"""

data.isnull().sum()

data.drop(["id", "key", "mode", "explicit"], axis=1, inplace=True)
data.head()

"""**Audio Correlation Analysis**"""

import matplotlib.pyplot as plt
import seaborn as sns

corr = data[["acousticness","danceability","energy", "instrumentalness",
             "liveness","tempo", "valence", "loudness", "speechiness"]].corr()

plt.figure(figsize=(10,10))
sns.heatmap(corr, annot=True)

""" # Audio Trends"""

avg_year = data[["acousticness","danceability","energy", "instrumentalness", 
               "liveness","tempo", "valence", "loudness", "speechiness", "year"]].\
groupby("year").mean().sort_values(by="year").reset_index()

avg_year.head()

"""# Line Plot (Trends in these variables)"""

plt.figure(figsize=(14,8))
plt.title("Song Trends Over Time", fontdict={"fontsize": 15})

lines = ["acousticness","danceability","energy", 
         "instrumentalness", "liveness", "valence", "speechiness"]

for line in lines:
    ax = sns.lineplot(x='year', y=line, data= avg_year)

    
plt.ylabel("value")
plt.legend(lines)

"""# Analyzing : Artist with the most number of songs"""

data["artists"].nunique() #Checking number of unique artists in the dataset

data["artists"].value_counts()[:10] #The Top 10 artists

artist_lt = data.artists.value_counts().index[:10] # Top 10 artists with the most number of songs 

dt_artists = data[data.artists.isin(artist_lt)][["artists","year"]].\
groupby(["artists","year"]).size().reset_index(name="song_count")

dt_artists.head()

plt.figure(figsize=(14,8))
sns.lineplot(x="year", y="song_count", hue="artists", data=dt_artists)

dt_artists.columns

artists_grp = data.groupby(['artists'])
Top20artists = artists_grp[['popularity']].sum().sort_values(by=['popularity'], ascending=False)[:20]
Top20artists.plot.barh(color='orange')
plt.title('Artists Popularity')
plt.xlabel('Popularity')
plt.ylabel('Artists')
plt.show()

top_artists = pd.DataFrame(np.zeros((100,10)), columns=artist_lt)
top_artists['year'] = np.arange(1921,2021)
print(top_artists.shape)
top_artists.head()

top_artists = top_artists.melt(id_vars='year',var_name='artists', value_name='song_count')
print(top_artists.shape)
top_artists.head()

Top10 = pd.DataFrame({'No of songs':dt_artists['artists'].value_counts().head(10)})
Top10.plot.bar(color='brown')
plt.title('Top 10 artists')
plt.xlabel('Artists')
plt.ylabel('No of song')
plt.show()

dt_merge = pd.merge(top_artists, dt_artists, on=['year','artists'], how='outer').\
sort_values(by='year').reset_index(drop=True)
dt_merge.head()

"""If an artist does not have any songs in a particular year, that value is filled with NaN. Let's also replace NaN values with 0 and drop song_count_x column."""

dt_merge.fillna(0, inplace=True)
dt_merge.drop('song_count_x', axis=1, inplace=True)
dt_merge.rename(columns={'song_count_y':'song_count'}, inplace=True)
dt_merge.head()

"""Adding a column that shows the cumulative sum of the songs that each artist produced over the years. One way to do that is to use groupby and cumsum functions."""

dt_merge['cumsum'] = dt_merge[['song_count','artists']].groupby('artists').cumsum()
dt_merge.head(10)

"""An animated bar plot that spans through the entire timeline to see how each artist dominates in different years.There will be a bar for each artists. The bars will go up as the cumulative number of songs for artists increase."""

# Commented out IPython magic to ensure Python compatibility.
import plotly.express as px

# %matplotlib inline

fig = px.bar(dt_merge, x='artists', y='cumsum', color='artists',
             animation_frame='year', animation_group='year',
             range_y=[0,1300],title='Artists with Most Songs')
fig.show()

"""# Recommendation System

**Importing the Data**
"""

artists_dt = pd.read_csv('/content/drive/MyDrive/data_by_artist.csv')
artists_dt = artists_dt.rename(columns={"count": "playCount"})

artists_dt.head(5)

artists_dt.columns

# Commented out IPython magic to ensure Python compatibility.
from sklearn.preprocessing import MinMaxScaler 
from sklearn.cluster import KMeans 
# %matplotlib inline

# we will replace each feature with its Genre for our convience and for easy tracking
scaler = MinMaxScaler()
artists_dt.iloc[:,1:-1] = scaler.fit_transform(artists_dt.iloc[:,1:-1])
km = KMeans(n_clusters=25)
artists_dt['genres'] = km.fit_predict(artists_dt.iloc[:,1:-1])
artists_dt = artists_dt.iloc[:,[0,-3,-2,-1]]
artists_dt.head()

artists_dt['user_id'] = np.random.randint(1000,1400,len(artists_dt))
artists_dt['rating'] = np.random.randint(1,6,len(artists_dt))
artists_dt.head()

artists_dt[(artists_dt['user_id']==1313) & (artists_dt['genres']==15)]

artists_dt.isna().sum()

def recommend_me(user):
    """This function will recommend artists to any user with its genre profile"""
    # first we will choose user top liked genres
    fav_genre = artists_dt[artists_dt['user_id']==user].sort_values(by=['rating','playCount'], ascending=False)['genres'][:5]
    fav_genre = list(dict.fromkeys(fav_genre))
      # lets clear out the artists from list whose songs has been listened by the user
    listened_artist = artists_dt.index[artists_dt['artists'].isin(['Johann Sebastian Bach','Fr??d??ric Chopin'])].tolist()
    
    # rest data
    remaining_artist = artists_dt.drop(listened_artist, axis=0)
    CanBeRecommened =  remaining_artist[remaining_artist['genres'].isin(fav_genre)]
    
    # now lets sort our artists whose are popular in this user favorite genre
    CanBeRecommened = CanBeRecommened.sort_values(by=['rating','playCount',], ascending=False)[['artists', 'genres', 'rating', 'playCount']][:5]
    
    # output will contain artists name, genres, other useres rating and song played count
    return CanBeRecommened

recommend_me(1313)

