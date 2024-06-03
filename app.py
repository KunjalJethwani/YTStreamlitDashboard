import streamlit as st
import plotly.express as px
import pandas as pd
import altair as alt

from helper import create_df, preprocess
from googleapiclient.discovery import build
from plots import plot_top_n_bar, title_word_cloud, year_views_line, heatmap, get_top_views, scatter_plot
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="YouTube Channel Analysis",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed")

alt.themes.enable("dark")

st.markdown("<h1 style='color: red; text-align: center;'>YouTube Channel Dashboard</h1>", unsafe_allow_html=True)

# st.title("YouTube Channel Dashboard")

api_key = st.text_input("Enter your YouTube API Key")
channel_id = st.text_input("Enter YouTube Channel ID") # use name

# api_key = 'AIzaSyD8f3mC8_FCn3HOjHhovAelZKK1b_LTd7s'
# channel_id = 'UC4JX40jDee_tINbkjycV4Sg' #use name

# api_service_name = "youtube"
# api_version = "v3"

# Get credentials and create an API client
if api_key and channel_id:
    
    # Get credentials and create an API client
    youtube = build("youtube", "v3", developerKey=api_key)
    
    # Fetch and preprocess data
    df = preprocess(create_df(youtube, [channel_id]))
        
    df_selected_sorted = get_top_views(df, 'viewCount', n=10)

    # Plot and display the chart
    col = st.columns((5, 7, 4.5), gap = 'medium')

    with col[0]:
        cols1 = st.columns((4, 8.5, 0.5))

        with cols1[1]:
            st.markdown('#### Top Viewed')
        # top_bot = st.columns((0.2, 1, 0.2))

        # with top_bot[1]:
        # st.altair_chart(plot_top_n_bar(df, 'title', 'viewCount', 10))


        st.dataframe(df_selected_sorted,
                    column_order=("title", "viewCount"),
                    hide_index=True,
                    width=850,
                    height = 300,
                    column_config={
                        "title": st.column_config.TextColumn(
                            "Title",
                        ),
                        "viewCount": st.column_config.ProgressColumn(
                            "Views",
                            format="%f",
                            min_value=0,
                            max_value=max(df_selected_sorted.viewCount),
                        )}
                    )

        st.altair_chart(scatter_plot(df))

    # increase width wrt ratio dist
    with col[1]:
        # top_bot = st.columns((3.5, 5, 0.5))
        top_bot = st.columns((4.5, 8.5, 0.5))

        with top_bot[1]:
            st.markdown('### Views per Year')
            
        st.altair_chart(year_views_line(df))

        # with top_bot[1]:
        #     st.write("")

        # with top_bot[1]:
        #     st.markdown('### Heatmap')
        # with top_bot[1]:
        #     st.markdown('### Heatmap')
        
        st.altair_chart(heatmap(df))

    # Increase col prop to shift left, fig width to increase right ways

    with col[2]:
        cols = st.columns((3.5, 7.5, 1))

        with cols[1]:
            st.markdown('### Major Titles')
        st.image(title_word_cloud(df))

        with st.expander('About', expanded=True):
                st.write('''
                    - :red[By]: Kunjal Jethwani
                    - :red[Description]: Provides insights into the performance of YouTube channels. Analyze metrics such as views, likes, and comments to gain a deeper understanding of channel engagement and audience behavior.
                    - :red[Contact]: For questions, feedback, or collaboration opportunities, please email kunjaljethwani@gmail.com.
                    - :red[Acknowledgements]: This project was developed using Streamlit for the web app interface and Altair for data visualization.
                    ''')
