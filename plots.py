import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud
import spacy
from helper import get_year

#====================================================================================================================
def get_top_views(df, y_col, n):
    df_sorted = df.sort_values(y_col, ascending=False).head(n)

    return df_sorted

#====================================================================================================

def plot_top_n_bar(df, x_col, y_col, n=9):

    """
    Plots a bar chart for the top N entries in the DataFrame sorted by y_col using Altair.

    Parameters:
    df (DataFrame): The input DataFrame.
    x_col (str): The column name for the x-axis.
    y_col (str): The column name for the y-axis.
    n (int): The number of top entries to display (default is 9).

    Returns:
    chart (alt.Chart): The Altair chart object.
    """
    
    # Sort the DataFrame and select top N entries
    df_sorted = df.sort_values(y_col, ascending=False).head(n)

    # Create the bar plot
    chart = alt.Chart(df_sorted).mark_bar().encode(
        y=alt.Y(x_col, sort='-x', title=None, axis=alt.Axis(labelAngle=0)),
        x=alt.X(y_col, title=None, axis=alt.Axis(format='~s')),
        tooltip=[x_col, y_col]
    ).properties(
        width=375,
        height=815,
        # title=f'Top {n} by {y_col.capitalize()}'
    ).configure_axis(title = None,
        labelAngle=90
    ).configure_title(
        fontSize=20,
        anchor='start',
        color='pink'
    )

    return chart

#============================================================================================================
import spacy

nlp = spacy.load("en_core_web_sm") 

def remove_stopwords_spacy(text):
    doc = nlp(text)
    
    return [token.text for token in doc if not token.is_stop]



def title_word_cloud(df, width=600, height=900, colormap='viridis'):
    """
    Generate a word cloud from the given text.

    Parameters:
    text (str): The text to generate the word cloud from.
    width (int): The width of the word cloud image (default is 2000).
    height (int): The height of the word cloud image (default is 1000).
    colormap (str): The name of the colormap to use (default is 'viridis').

    Returns:
    wordcloud_image (numpy.ndarray): The generated word cloud image.
    """
    df['title_no_stopwords'] = df['title'].apply(lambda x: remove_stopwords_spacy(x))

    all_words = list([a for b in df['title_no_stopwords'].tolist() for a in b])
    all_words_str = ' '.join(all_words) 


    wordcloud = WordCloud(width = 600, height = 750, random_state=1, background_color=None, mode='RGBA', 
                        colormap='gist_heat', collocations=False).generate(all_words_str)


    return wordcloud.to_array()

#==================================================================================================================

def year_views_line(df):

    df['publishedYear'] = df['publishedAt'].apply(get_year)
    year_wise_count = df.groupby('publishedYear')['viewCount'].sum()
    df_yearly = year_wise_count.reset_index()
    df_yearly['publishedYear'] = df_yearly['publishedYear'].apply(str)

    x_col = 'publishedYear'
    y_col = 'viewCount'


    # Create the bar plot
    chart = alt.Chart(df_yearly).mark_line(color='red').encode(
        y=alt.Y(y_col, title=None, axis=alt.Axis(format='~s')),
        x=alt.X(x_col, title=None, axis=alt.Axis(labelAngle=0)),
        tooltip=[x_col, y_col]
    ).properties(
        width=550,
        height=300,
    ).configure_axis(title = None,
        labelAngle=90
    ).configure_title(
        fontSize=20,
        anchor='start'
    )
    return chart

#================================================================================================================

def scatter_plot(df):
    scatter_plot = alt.Chart(df).mark_circle(size=60, color='red').encode(
        x=alt.X('viewCount:Q', title='Views', axis=alt.Axis(format='~s')),
        y=alt.Y('likeCount:Q', title='Likes', axis=alt.Axis(format='~s')),
        tooltip=['viewCount', 'likeCount']
    ).properties(
        width=375,
        height=350
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=20,
        anchor='start'
    )

    return scatter_plot



#==============================================================================================================

def hist(df):

    histogram = alt.Chart(df).mark_bar().encode(
    alt.X('durationSecs:Q', bin=True, title='Duration (Secs)'),
    alt.Y('count()', title='Number of Videos'),
    tooltip=['count()']
    ).properties(
    width=400,
    height=300,
    title='Histogram of Duration'
    )

    return histogram


#================================================================================================================

def heatmap(df):
    df['publishedAt'] = pd.to_datetime(df['publishedAt'])

    # Extract day of the week and hour
    df['day_of_week'] = df['publishedAt'].dt.day_name()
    df['hour'] = df['publishedAt'].dt.hour

    # Map full day names to abbreviations
    day_abbr = {
        'Monday': 'Mon',
        'Tuesday': 'Tue',
        'Wednesday': 'Wed',
        'Thursday': 'Thu',
        'Friday': 'Fri',
        'Saturday': 'Sat',
        'Sunday': 'Sun'
    }
    df['day_of_week_abbr'] = df['day_of_week'].map(day_abbr)

    # Aggregate data to count the number of videos published at each day-hour combination
    heatmap_data = df.groupby(['day_of_week_abbr', 'hour']).size().reset_index(name='count')

    # Custom sorting order for days of the week
    day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    # Create the heatmap using Altair
    heatmap = alt.Chart(heatmap_data).mark_rect().encode(
        x=alt.X('hour:O', title='Hour of Day'),
        y=alt.Y('day_of_week_abbr:O', title=None, sort=day_order),
        color=alt.Color('count:Q', scale=alt.Scale(scheme='reds'), title='No of Vids'),
        tooltip=['day_of_week_abbr', 'hour', 'count']
    ).properties(
        width=550,
        height=350,
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=20,
        anchor='start'
    )

    return heatmap

