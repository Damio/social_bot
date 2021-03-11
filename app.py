from flask import Flask, request, url_for, render_template, redirect, abort, flash, jsonify
from models import MyTweets, RedditPost
from mongoengine import connect
from datetime import datetime

from twitter import *
# reddit connection
import praw

# database and twitter connection
from config import DB_URI, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, R_CLIENT_ID, R_CLIENT_SECRET, R_USER_AGENT, R_USERNAME, R_PASSWORD


app = Flask(__name__)   # create our flask app

# database auth
connect('TwitterFeeds', host=DB_URI)

# twitter authentication
#configure Twitter API
twitter = Twitter(
            auth=OAuth(
                ACCESS_TOKEN, 
                ACCESS_TOKEN_SECRET,
                CONSUMER_KEY, 
                CONSUMER_SECRET
                )  
           )


# reddit config
reddit = praw.Reddit(
    client_id=R_CLIENT_ID,
    client_secret=R_CLIENT_SECRET,
    user_agent=R_USER_AGENT,
    username=R_USERNAME,
    password=R_PASSWORD
)
reddit.validate_on_submit=True



@app.route('/')
def posts():
    tweets = MyTweets.objects()
    reddit_posts = RedditPost.objects()
    return render_template("posts.html", tweets=tweets, reddit_posts=reddit_posts)

@app.route('/twitterpost', methods=['GET','POST'])
def post_to_twitter():


    if request.method == 'POST':
        # gets the tweet from the webpage
        status = request.form.get('status')

        # update twitter with the status
        tweet = twitter.statuses.update(status=status)

        # store data in db
        my_tweet = MyTweets(
            text = tweet["text"],
            language = tweet["lang"],
            favorite_count = tweet["favorite_count"],
            created_at = tweet["created_at"],
            username = tweet["user"]["screen_name"]
        )
        my_tweet.save()
		# redirect to new twitter status post
        return redirect('http://www.twitter.com/%s/status/%s' % (tweet['user']['screen_name'], tweet.get('id')))
        #return render_template('index.html')
    else:
        return redirect(url_for("posts"))

@app.route('/redditpost', methods=['GET','POST'])
def post_to_reddit():
    if request.method == 'POST':
        # get data from front end
        title = request.form.get('title')
        selftext = request.form.get('status')
        subr = request.form.get('subr')

        # connect to the subreddit
        subreddit = reddit.subreddit(subr)

        # send the post to reddit
        post = subreddit.submit(title,selftext=selftext)
        
        # convert time
        ts = int(post.created_utc)

        # if you encounter a "year is out of range" error the timestamp
        # may be in milliseconds, try `ts /= 1000` in that case
        created_utc=datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        # extract data from reddit respon
        # save to database
        reddit_post = RedditPost(
            text=selftext,
            title=title,
            num_comments=post.num_comments,
            created_utc=created_utc,
            author=post.author.name
        )

        reddit_post.save()
        new_title = "_".join(title.split(" "))
        # try redirect to reddit to see the post
        return redirect(f"https://www.reddit.com/r/{subr}/comments/{post.id}/{new_title}/")

        # https://www.reddit.com/r/Fish/comments/loi9iy/lets_go_fishing3/

        return redirect(url_for("posts"))

if __name__ == "__main__":
    app.run(debug=True)