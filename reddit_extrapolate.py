from datetime import datetime, timedelta

def from_dict_to_sorted_list(dictionary_to_sort):
    sorted_keys = []
    sorted_counts = []
    for i in range(len(dictionary_to_sort.keys())):
        sorted_keys.append("")
        sorted_counts.append(0)
        if i == 0:
            for key in dictionary_to_sort.keys():
                total_counts = dictionary_to_sort[key]
                if total_counts > sorted_counts[i]:
                    sorted_counts[i] = total_counts
                    sorted_keys[i] = key
        else:
            for key in dictionary_to_sort.keys():
                total_counts = dictionary_to_sort[key]
                if total_counts > sorted_counts[i] and total_counts <= sorted_counts[i-1] and key not in sorted_keys:
                    sorted_counts[i] = total_counts
                    sorted_keys[i] = key
    return sorted_keys, sorted_counts


class RedditSubreddit:
    def __init__(self, subscriber_count=0, list_of_posts=[]):
        self.popularity = subscriber_count
        self.posts = list_of_posts

    def get_comments_as_list(self, posts_list=None):
        if posts_list == None:
            posts_list = self.posts
        full_list_of_comments = []
        for post in posts_list:
            comments = post.comments
            for comment in comments:
                full_list_of_comments.append(comment)
        return full_list_of_comments


    def add_update_posts(self, additional_posts):
        post_ids = []
        for post in self.posts:
            post_ids.append(post.id)
        for post in additional_posts:
            #Append if not already captured
            if not post.id in post_ids:
                self.posts.append(post)
            #Update if already tracked
            else:
                self.posts[post_ids.index(post.id)] = post

    def dated_get_posts(self, earliest_date):
        latest_date = earliest_date + timedelta(days=1)
        dated_post_list = []
        for post in self.posts:
            if earliest_date <= post.date <= latest_date:
                dated_post_list.append(post)
        return dated_post_list

    def get_top_poster(self, n=1, posts_list=None):
        if n < 1:
            n = 1
        if posts_list == None:
            posts_list = self.posts
        if n > len(posts_list):
            n = len(posts_list)
        ranked_posts = dict()
        for post in posts_list:
            if post.author in ranked_posts.keys():
                ranked_posts[post.author] = ranked_posts[post.author] + post.karma
            else:
                ranked_posts[post.author] = post.karma
        [sorted_authors, sorted_upvote_counts] = from_dict_to_sorted_list(ranked_posts)
        return sorted_authors[min(len(ranked_posts)-1, n-1)]

    def dated_get_top_poster(self, earliest_date, n=1):
        dated_post_list = self.dated_get_posts(earliest_date)
        if not dated_post_list:
            return None
        else:
            return self.get_top_poster(n=n, posts_list=dated_post_list)

    def get_top_commenter(self, n=1, posts_list=None):
        if n < 1:
            n = 1
        if posts_list == None:
            posts_list = self.posts
        full_list_of_comments = self.get_comments_as_list(posts_list=posts_list)
        if n > len(full_list_of_comments):
            n = len(full_list_of_comments)
        ranked_comments = dict()
        for comment in full_list_of_comments:
            if comment.author in ranked_comments.keys():
                ranked_comments[comment.author] = ranked_comments[comment.author] + comment.karma
            else:
                ranked_comments[comment.author] = comment.karma
        [sorted_authors, sorted_upvote_counts] = from_dict_to_sorted_list(ranked_comments)
        return sorted_authors[min(len(sorted_authors)-1, n-1)]

    def dated_get_top_commenter(self, earliest_date, n=1):
        dated_post_list = self.dated_get_posts(earliest_date)
        if not dated_post_list:
            return None
        else:
            return self.get_top_commenter(n=n, posts_list=dated_post_list)

class RedditPost:
    def __init__(self, post_object): 
        self.author = post_object.author.name
        self.subreddit = post_object.subreddit.display_name
        self.title = post_object.title
        self.date = datetime.fromtimestamp(post_object.created)
        self.id = post_object.id
        self.comments = []
        self.karma = post_object.ups

    def setCommentList(self, list_of_comments):
        self.comments = list_of_comments

class RedditComment:
    def __init__(self, comment_object): 
        self.author = comment_object.author.name
        self.subreddit = comment_object.subreddit.display_name
        self.date = datetime.fromtimestamp(comment_object.created)
        self.id = comment_object.id
        self.content = comment_object.body
        self.karma = comment_object.ups
