import json

from with_db import *

def separate_tweet_find_tweetcode(tweets):
    '''
    The function for separate tweets and return only tweet codes
    :param tweets: string from post resuest with one or several tweets
    :return: only tweet codes
    '''
    res = []
    all_tweets = tweets.split('https://twitter.com')
    for tweet in all_tweets:
        if tweet.split('/')[-1]:
            res.append(tweet.split('/')[-1])
    return res




