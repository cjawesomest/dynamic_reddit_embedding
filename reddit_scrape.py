#For Reddit API
import praw
from praw.models import MoreComments
from praw.models import Redditor
from praw.models import Subreddit
from prawcore.exceptions import Redirect as RedirectException
from prawcore.exceptions import Forbidden as ForbiddenException
from prawcore.exceptions import NotFound as NotFoundException
from prawcore.exceptions import BadRequest as BadRequestException
from prawcore.exceptions import TooLarge as TooLargeException
from prawcore.exceptions import RequestException
reddit = praw.Reddit("CJ")

#Data structures for keeping track
from reddit_extrapolate import RedditSubreddit, RedditPost, RedditComment

#Exceptions
known_exceptions = (RedirectException, ForbiddenException, NotFoundException, BadRequestException)

#For REGEX
import re 

import sys

from datetime import datetime, timedelta

DEBUG = 1



#Deprecated
def get_popularity(subreddit_name):
    # reddit = praw.Reddit("CJ")
    try:
        if is_valid(subreddit_name, reddit):
            subreddit = reddit.subreddit(subreddit_name)
            submissions = subreddit.hot(limit=2)
            return subreddit.subscribers
        else:
            return 1
    except:
        print('Unknown Exception searching for r/'+subreddit_name+': Moving on...'+str(sys.exc_info()[0]))
        return 1


#If the subreddit is valid, it will not have a problem accessing its name
def is_valid(some_reddit_object):
    try:
        if isinstance(some_reddit_object, Subreddit):
            name_or_redirect = some_reddit_object.fullname
            # if(DEBUG):
            #     print(name_or_redirect)
            return 1
        if isinstance(some_reddit_object, Redditor):
            if hasattr(some_reddit_object, 'is_suspended'):
                return 0
            else:
                name_or_redirect = some_reddit_object.fullname
                return 1
    except known_exceptions:
        return 0
    except RecursionError:
        print('That\'s a lot of comments! Probably a bot...')
        return 0


    

#Deprecated
def find_linked_subreddits(subreddit_name, reddit_credentials=None):
    #Some variables
    #Find comments that are just links to other subreddits using regex
    regex = "^r/"
    #Limit the number of comments to search on every post
    global_comment_limit = None
    global_more_comments_threshold = 10
    #Limit the number of posts on the subreddit to search
    global_submission_limit = 100

    #Keep track of found subreddits
    found_reddits = []

    #Obtain credentials if not already specified
    # if reddit_credentials == None:
    #     reddit = praw.Reddit("CJ")
    #     reddit.read_only = True
    # else:
    #     reddit = reddit_credentials

    #Obtain specified subreddit, keeping in mind that it may not exist
    subreddit = reddit.subreddit(subreddit_name)
    # print(subreddit.display_name)  # Output: redditdev
    # print(subreddit.title)         # Output: reddit Development
    # print(subreddit.description)   # Output: A subreddit for discussion of ...

    #Grab some content!
    #Search for comments that directly link to other subreddits
    print('Commencing the search for subreddits! Now: r/'+subreddit_name)
    try:
        all_hot_submissions = subreddit.hot(limit=global_submission_limit)
        for submission in all_hot_submissions:
            submission.comments.replace_more(limit=global_comment_limit, threshold=global_more_comments_threshold)
            all_comments = submission.comments.list()
            # print(submission.title)
            for comment in all_comments:
                if(isinstance(comment, MoreComments)):
                    continue
                else:
                    if not re.search(regex, comment.body) == None and len(comment.body.split()) == 1:
                        #Take only the first word (the next subreddit)
                        comment_total = comment.body.split()
                        r_slash = comment_total[0]
                        r_slash_name = r_slash.split("/")[1]
                        #Add repeats to the list, the outer program will keep track of things
                        is_valid_subreddit = is_valid(r_slash_name, reddit)
                        is_already_tracked = r_slash_name.lower() == subreddit_name or\
                            r_slash_name.lower() in [low_case.lower() for low_case in found_reddits]
                        if is_valid_subreddit: #and not is_already_tracked:
                            if is_already_tracked:
                                print('\t(REPEAT) r/'+r_slash_name)
                            else:
                                print('\tr/'+r_slash_name)
                            found_reddits.append(r_slash_name.lower())
                        # elif is_valid_subreddit and is_already_tracked:
                        #     print('\t(REPEAT) r/'+r_slash_name)
                        elif not is_valid_subreddit:
                            print('\t(INVALID) r/'+r_slash_name)
                        # elif not is_valid(r_slash_name, reddit)\
                        # and not r_slash_name.lower() in [low_case.lower() for low_case in found_reddits]:
                        #     print('\tr/'+r_slash_name+'(INVALID)')
                        #     found_reddits.append('(INVALID)'+r_slash_name.lower())  
    except known_exceptions: 
        print('[INVALID SUBREDDIT #subsifellfor] Now: r/'+subreddit_name)
        return found_reddits
    except KeyboardInterrupt:
        SystemExit
    except:
        print('Unknown Exception: Moving on...'+str(sys.exc_info()[0]))
        return found_reddits
    return found_reddits

#New Functions: Try to Use These Instead

#Find all comments on a post that were created before a particular date
#Returns a list of RedditComment objects
def dated_post_query(post_object, latest_date, number_of_comments=100, more_comments_thresh=5):
    try:
        post_object.comments.replace_more(limit=more_comments_thresh, threshold=more_comments_thresh)
    except (TooLargeException, RequestException, AssertionError):
        #This happens because my HTTP request is too large and Reddit doesn't give it to me!
        #That's alright because there is usually more than enough info even without all of the comments
        pass
    # except:
    #     error_type, error_value, traceback = sys.exc_info()
    #     print('Error: %s: %s' % (error_value.filename, error_value.strerror))
    #     pass
    all_comments = post_object.comments.list()
    comment_list = []
    for comment in all_comments:
        if(isinstance(comment, MoreComments)):
            continue
        else:
            comment_time = datetime.fromtimestamp(comment.created)
            if comment_time < latest_date:
                if comment.author == None:
                    continue
                comment_representation = RedditComment(comment)
                comment_list.append(comment_representation)
            else:
                continue
        if len(comment_list) >= number_of_comments:
            break
    return comment_list

#Find the posts on a subreddit on a particular day
#If no latest_date is specified, only searches on one day (24 hours)
#Providing a latest_date searches for an inclusive range between earliest_date and latest_date
#Changing the number_of_posts changes how many posts are received at maximum for any day
#Returns the RedditSubreddit
def dated_subreddit_query(subreddit_name, earliest_date, latest_date=None, number_of_posts=20):
    subreddit = reddit.subreddit(subreddit_name)
    if(is_valid(subreddit)):
        #Get the subscriber count
        subscriber_count = subreddit.subscribers

        #Determine search timeframe
        time_delta = datetime.now()-earliest_date
        if latest_date == None:
            latest_date = earliest_date + timedelta(days=1)
        if time_delta.days < 1: temporal_filter = 'day'
        elif time_delta.days <= 7: temporal_filter = 'week'
        elif time_delta.days <= 28: temporal_filter = 'month'
        elif time_delta.days <= 365: temporal_filter = 'year'
        else: temporal_filter = 'all'
        timed_posts = subreddit.search("subreddit:"+subreddit_name, sort='top', time_filter=temporal_filter, limit=None)
        
        #Find posts within timeframe
        list_of_posts = []
        for submission in timed_posts:
            post_date = datetime.fromtimestamp(submission.created)
            if earliest_date <= post_date <= latest_date:
                if submission.author == None:
                    continue
                comments_list = dated_post_query(submission, latest_date)
                post_representation = RedditPost(submission)
                post_representation.setCommentList(comments_list)
                list_of_posts.append(post_representation)
                if len(list_of_posts) >= number_of_posts:
                    break
            else:
                continue
        return RedditSubreddit(subscriber_count, list_of_posts)
    else:
        return None

def dated_user_query(username, earliest_date, latest_date=None, number_of_posts=20, number_of_comments=50):
    user = reddit.redditor(username)
    if is_valid(user):
        if latest_date == None:
            latest_date = earliest_date + timedelta(days=1)
        timed_posts = user.submissions.new(limit=None)
        list_of_posts = []
        for submission in timed_posts:
            post_date = datetime.fromtimestamp(submission.created)
            if earliest_date <= post_date <= latest_date:
                comments_list = dated_post_query(submission, latest_date)
                post_representation = RedditPost(submission)
                post_representation.setCommentList(comments_list)
                list_of_posts.append(post_representation)
                if len(list_of_posts) >= number_of_posts:
                    break
            else:
                continue
        timed_comments = user.comments.new(limit=None)
        list_of_comments=[]
        for comment in timed_comments:
            comment_time = datetime.fromtimestamp(comment.created)
            if earliest_date <= comment_time <= latest_date:
                comment_representation = RedditComment(comment)
                list_of_comments.append(comment_representation)
                if len(list_of_comments) >= number_of_comments:
                    break
            else:
                continue
        return list_of_posts, list_of_comments
    else:
        return None

if __name__ == "__main__":
    start='nostupidquestions'
    sub_info = dated_subreddit_query(start, datetime(2020, 5, 17))
    print(sub_info.get_top_poster(n=100))
    print(sub_info.dated_get_top_poster(datetime(2020, 5, 18), n=100))
    print(sub_info.get_top_commenter(n=100))
    print(sub_info.dated_get_top_commenter(datetime(2020, 5, 18), n=100))
    sub_info_tomorrow = dated_subreddit_query(start, datetime(2020, 5, 18))
    sub_info.add_update_posts(sub_info_tomorrow.posts)
    print(sub_info.get_top_poster(n=100))
    print(sub_info.dated_get_top_poster(datetime(2020, 5, 18), n=100))
    print(sub_info.get_top_commenter(n=100))
    user_top_commenter = sub_info.dated_get_top_commenter(datetime(2020, 5, 18), n=100)
    # user_top_commenter = "punchkitty"
    print(user_top_commenter)
    print(dated_user_query(user_top_commenter, datetime(2020, 5, 18)))
    print('yay')

    