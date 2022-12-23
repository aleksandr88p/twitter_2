from flask import Flask, url_for, render_template, request
from funcs import *
from twitter import *



app = Flask(__name__)
import json

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == 'POST' and 'tweetLink' in request.form:
        try:
            headers = {
                'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.{random.randint(0, 9999)} Safari/537.{random.randint(0, 99)}',
                'x-guest-token': ''
            }
            print(headers)
            x_guest = update_guest_token(headers=headers)
            headers['x-guest-token'] = x_guest
            print(headers)
            tweet_codes = separate_tweet_find_tweetcode(str(request.form.get("tweetLink")))
            print(tweet_codes)
            tweetsss = json_to_show(tweet_codes, headers=headers)
            headers['x-guest-token'] = ''

        except Exception as e:
            tweetsss = f"""unexpected format, please use format like\nhttps://twitter.com/Birgit_Mager/status/1495354761876541441"""
            return render_template('index.html', pre_json=tweetsss)

        return render_template('index.html', pre_json=json.dumps(tweetsss, indent=4))

    return render_template('index.html', pre_json='empty')



# for deploy you can use this
# if __name__ == '__main__':
#     app.run(debug=False, port=5555)

# or you can use this http://127.0.0.1:1234/
if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=1234)