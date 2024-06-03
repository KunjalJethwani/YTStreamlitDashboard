import pandas as pd
import isodate
from dateutil import parser
from IPython.display import JSON
from googleapiclient.discovery import build

# Data viz packages
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# NLP
import nltk
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# nltk.download('stopwords')
# nltk.download('punkt')
import datetime
from datetime import datetime
#===========================================================================================================

def get_channel_stats(youtube, channel_id):

    all_data = []
    
    request = youtube.channels().list(
        part="snippet, contentDetails, statistics",
        id=','.join(channel_id)
        )
    response = request.execute()

    for item in response['items']:
        data = {'channelName' : item['snippet']['title'],
                'subscribers' : item['statistics']['subscriberCount'],
                'views' : item['statistics']['viewCount'],
                'totalVideos' : item['statistics']['videoCount'],
                'playlistId' : item['contentDetails']['relatedPlaylists']['uploads']
               }
        
    all_data.append(data)

    return pd.DataFrame(all_data)

#---------------------------------------------------------------------------------------------------------

# Extracting all vid ids
def get_video_ids(youtube, playlist_id):

    video_ids = []
    request = youtube.playlistItems().list(
            part="snippet, contentDetails",
            playlistId = playlist_id,
            maxResults = 50
    )
    
    response = request.execute()
    
    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])

    next_page_token = response.get('nextPageToken')

    while next_page_token is not None:
        
        request = youtube.playlistItems().list(
            part="snippet, contentDetails",
            playlistId = playlist_id,
            maxResults = 50,
            pageToken = next_page_token
        )
        response = request.execute()
        
        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')
    
    response = request.execute()
    return video_ids

#-------------------------------------------------------------------------------------------------------------

# Vid Info from above vid ids
def get_video_details(youtube, video_ids):
    
    all_video_info = []

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
                part = "snippet, contentDetails, statistics",
                id = ','.join(video_ids[i:i+50])
        )
        response = request.execute()
    
        for video in response['items']:
            stats_to_keep = {'snippet' : ['channelTitle', 'title', 'description', 'tags', 'publishedAt'],
                             'statistics' : ['viewCount', 'likeCount', 'favouriteCount', 'commentCount'],
                             'contentDetails' : ['duration', 'definition', 'caption']
                            }
        
            video_info = {}
            video_info['video_id'] = video['id']
    
            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:

                    try:
                        video_info[v] = video[k][v]

                    except:
                        video_info[v] = None
                        
            all_video_info.append(video_info)
        
    return pd.DataFrame(all_video_info)

#------------------------------------------------------------------------------------------------------------

def get_comments_in_videos(youtube, video_ids):
    
    all_comments = []
    
    for video_id in video_ids:

        try:        
            request = youtube.commentThreads().list(
                    part="snippet, replies",
                    videoId = video_id
            )
            response = request.execute()
    
            comments_in_video = [comment['snippet']['topLevelComment']['snippet']['textOriginal'] for comment in response['items'][0:10]]
            comments_in_video_info = {'video_id' : video_id, 'comments' : comments_in_video}
            
        except:
            comments_in_video_info = {'video_id' : video_id, 'comments' : []}

        all_comments.append(comments_in_video_info)

    return pd.DataFrame(all_comments)

def create_df(youtube, channel_id):

    channel_stats = get_channel_stats(youtube, channel_id)
    playlist_id = channel_stats['playlistId'][0]
    video_ids = get_video_ids(youtube, playlist_id)
    vid_df = get_video_details(youtube, video_ids)
    vid_df = vid_df.merge(get_comments_in_videos(youtube, video_ids), on = 'video_id')

    return vid_df

num_cols = ['viewCount', 'likeCount', 'favouriteCount', 'commentCount']
def preprocess(df):

    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors = 'coerce', axis = 1)

    df['publishedAt'] = df['publishedAt'].apply(lambda x : parser.parse(x))
    df['publishDayName'] = df['publishedAt'].apply(lambda x : x.strftime('%A'))

    df['durationSecs'] = df['duration'].apply(lambda x : isodate.parse_duration(x))
    df['durationSecs'] = df['durationSecs'].astype('timedelta64[s]')

    df['tagCount'] = df['tags'].apply(lambda x: 0 if x is None else len(x))

    return df
#====================================================================================================

def get_year(x):
    '''
    Converts a datetime object or ISO format string to year.
    '''
    # Check if the input is already a datetime object
    if isinstance(x, datetime):
        datetime_obj = x

    else:
        # Parse the datetime string into a datetime object
        datetime_obj = datetime.strptime(x, "%Y-%m-%d %H:%M:%S%z")

    # Extract the year from the datetime object
    year = datetime_obj.year

    return year
