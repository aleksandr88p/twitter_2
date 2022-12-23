import json
import random
import itertools
import email.utils
import requests
import shutil
from with_db import *


# params for post request in tweeter
params = {
    'include_profile_interstitial_type': '1',
    'include_blocking': '1',
    'include_blocked_by': '1',
    'include_followed_by': '1',
    'include_want_retweets': '1',
    'include_mute_edge': '1',
    'include_can_dm': '1',
    'include_can_media_tag': '1',
    'skip_status': '1',
    'cards_platform': 'Web-12',
    'include_cards': '1',
    'include_ext_alt_text': 'true',
    'include_quote_count': 'true',
    'include_reply_count': '1',
    'tweet_mode': 'extended',
    'include_entities': 'true',
    'include_user_entities': 'true',
    'include_ext_media_color': 'true',
    'include_ext_media_availability': 'true',
    'send_error_codes': 'true',
    'simple_quoted_tweet': 'true',
    'count': '20',
    'include_ext_has_birdwatch_notes': 'false',
    'ext': 'mediaStats,highlightedLabel',
}

base_url = 'https://twitter.com'
base_api_url = 'https://api.twitter.com'


def update_guest_token(headers):
    """
    function for get guest token for scrape data
    :return: function write guest token in headers
    """
    try:
        response = requests.post(url=f"{base_api_url}/1.1/guest/activate.json", headers=headers,
                                 data=b'')
        if response is None:
            print('bad proxie')
        if response.status_code in [200]:
            j_son = response.json()
            return j_son['guest_token']
            # headers.update({'x-guest-token': j_son['guest_token']})
    except Exception as ex:
        print(ex)
        update_guest_token(headers=headers)


def return_tweet(endpoint, params, headers):
    print('start return_tweet')
    """
    function for get the all information from tweet in json format
    :param endpoint: url with tweet in format
    https://twitter.com/i/api/2/timeline/conversation/{tweet_code}.json
    :param params: params
    :param headers: headers 
    :return: json with information from tweet
    """
    response = requests.get(url=endpoint, params=params, headers=headers)
    print(response)
    try:
        obj = response.json()
    except Exception as e:
        print(e)
        obj = None
    return obj


def render_text_with_url(text, urls):
    """
    :param text: full_text from tweet
    :param urls: urls from tweet
    :return:
    """
    if not urls:
        return text
    out = list()
    out.append(text[:urls[0]['indices'][0]])
    # print(text[:urls[0]['indices'][0]])  # todo потом удалить
    assert all(url['indices'][1] <= nextUrl['indices'][0] for url, nextUrl in zip(urls, urls[1:])), 'broken URL indices'
    for url, nextUrl in itertools.zip_longest(urls, urls[1:]):
        if 'display_url' in url:
            out.append(url['display_url'])
        out.append(text[url['indices'][1]: nextUrl['indices'][0] if nextUrl is not None else None])
    return ''.join(out)



def info_from_tweet(tweet, obj):
    '''
    add headers in paranetrs if need to scrape foto and video
    :param obj: what returned response with ... obj['globalObjects']['tweets'][str(tweetId)
    :param tweet: just obj
    :return: dict with info
    '''
    kwargs = {}
    kwargs['id'] = tweet['id'] if 'id' in tweet else int(tweet['id_str'])
    kwargs['content'] = tweet['full_text']
    kwargs['renderedContent'] = render_text_with_url(tweet['full_text'], tweet['entities'].get('urls'))
    kwargs['date'] = str(email.utils.parsedate_to_datetime(tweet['created_at']))
    kwargs[
        'url'] = f'https://twitter.com/{obj["globalObjects"]["users"][tweet["user_id_str"]]["screen_name"]}/status/{kwargs["id"]}'
    kwargs['replyCount'] = tweet['reply_count']
    kwargs['retweetCount'] = tweet['retweet_count']
    kwargs['likeCount'] = tweet['favorite_count']
    kwargs['quoteCount'] = tweet['quote_count']
    kwargs['conversationId'] = tweet['conversation_id'] if 'conversation_id' in tweet else int(
        tweet['conversation_id_str'])

    #############################
    # BLOCK links, hashtags etc #
    #############################
    if tweet['entities'].get('urls'):
        kwargs['links'] = [l['expanded_url'] for l in tweet['entities']['urls']]
    if tweet['entities'].get('hashtags'):
        kwargs['hashtags'] = [o['text'] for o in tweet['entities']['hashtags']]
    if tweet['entities'].get('symbols'):
        kwargs['symbols'] = [o['text'] for o in tweet['entities']['symbols']]

    ##############
    # USER BLOCK #
    ##############
    from_user = obj['globalObjects']['users'][tweet['user_id_str']]
    # kwargs['user_id_str'] = tweet.get('user_id_str', 0)
    kwargs['tweeter_handle'] = from_user['screen_name']
    kwargs['author_name'] = from_user['name']
    kwargs['description'] = from_user['description']

    ###############
    # BLOCK MEDIA #
    ###############
    if 'extended_entities' in tweet and 'media' in tweet['extended_entities']:
        media = []
        c = 0
        for medium in tweet['extended_entities']['media']:
            if medium['type'] == 'photo':
                if '.' not in medium['media_url_https']:
                    continue
                base_foto_url, image_format = medium['media_url_https'].rsplit('.', 1)
                if image_format not in ('jpg', 'png'):
                    print(f'Skipping foto with unknown format on tweet {kwargs["id"]}')
                media.append({'format': image_format, 'url': f'{base_foto_url}?format={image_format}&name=large'})
            elif medium['type'] == 'video' or medium['type'] == 'animated_gif':
                variants = []
                # there are several variants with different bitrate
                for variant in medium['video_info']['variants']:
                    variants.append({'content_type': variant['content_type'], 'url': variant['url'],
                                     'bitrate': variant.get('bitrate')})
                media.append(variants[0])

        if media:
            kwargs['media'] = media
    return kwargs


def find_tweetcodes_from_file(file_path=None, tweeturl=None):
    """
    :param file_path: path to file in format txt with tweet urls
    :param tweeturl: one tweet url
    :return: list with tweet codes
    """
    tweet_codes = []
    if file_path:
        with open(file_path, 'r') as file:
            all_tweets = file.readlines()
            for tweet in all_tweets:
                tweet = tweet.replace('\n', '')
                try:
                    tweet_codes.append(tweet.split('/')[-1])
                except Exception as e:
                    print(f'no in find_tweetcodes_from_file\n{e}')
    if tweeturl:
        try:
            tweeturl = tweeturl.replace('\n', '')
            tweet_codes.append(tweeturl.split('/')[-1])
        except Exception as e:
            print(f'unexpected format of tweet\n{e}')

    return tweet_codes


def main_func(tweet_code, headers):
    print('in main func', tweet_code)

    url = f'https://twitter.com/i/api/2/timeline/conversation/{tweet_code}.json'
    print(headers)
    print(url)
    print(params)
    ans = return_tweet(endpoint=url, params=params, headers=headers)
    some_info_from_tweet = info_from_tweet(ans['globalObjects']['tweets'][tweet_code], ans)
    write_from_json_to_db(some_info_from_tweet)
    return some_info_from_tweet


def json_to_show(tweet_codes, headers):
    print('in headers')
    print(headers)
    '''
    make a dict to show in site
    :param tweet_codes:
    :return:
    '''
    tweetsss = {}
    for i, code in enumerate(tweet_codes):
        print('in cycle')
        print(headers)
        tweet_to_db = main_func(code, headers=headers)
        tweetsss.update({i: tweet_to_db})
    return tweetsss
