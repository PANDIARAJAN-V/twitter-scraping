
import snscrape.modules.twitter as sntwitter
import pandas as pd
import streamlit as st
import pymongo

def scrape_tweets(keyword, start_date, end_date, tweet_count):

    tweets_list = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'{keyword} since:{start_date} until:{end_date}').get_items()):
        if i >= tweet_count:
            break
        tweets_list.append([tweet.date, tweet.id, tweet.url, tweet.content, tweet.user.username, tweet.replyCount, tweet.retweetCount, tweet.lang, tweet.sourceLabel, tweet.likeCount])
    
    df = pd.DataFrame(tweets_list, columns=['Date', 'ID', 'URL', 'Content', 'User', 'Reply Count', 'Retweet Count', 'Language', 'Source', 'Like Count'])
    return df



def insert_to_mongodb(df, collection_name, keyword):
 
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    

    db = client["twitter_data"]
    collection = db[collection_name]
    

    data_dict = df.to_dict(orient='records')
    for data in data_dict:
        data["Scraped Word"] = keyword
        collection.insert_one(data)



st.title('Twitter Scraper')


keyword = st.text_input('Enter the keyword to search')
start_date = st.date_input('Start date')
end_date = st.date_input('End date')
tweet_count = st.number_input('Enter the number of tweets to scrape')


if st.checkbox('Scrape'):
    tweets = scrape_tweets(keyword, (start_date),(end_date), tweet_count)
    df = pd.DataFrame(tweets)
    st.write(df)
    if st.button('Upload to MongoDB'):
        store_tweets_in_db(tweets, keyword)
        st.write('Data uploaded to MongoDB!')
    if st.button('Download as CSV'):
        csv = df.to_csv(index=False)
        st.download_button('Download CSV', data=csv, file_name=f'{keyword}.csv', mime='text/csv')
    if st.button('Download as JSON'):
        json = df.to_json(orient='records')
        st.download_button('Download JSON', data=json, file_name=f'{keyword}.json', mime='application/json')
