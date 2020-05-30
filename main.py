import pickle
import os.path

from datetime import datetime, timedelta
from reddit_scrape import *
from reddit_io import *
from embedded_plot import *

import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    #Configure variables for program running
    # subreddit_request = "NoStupidQuestions"
    subreddit_request = "AskReddit" 
    today_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
    yesterday_date = today_date - timedelta(days=1)
    number_of_days_retro = 14 #Default 14
    earliest_date = yesterday_date - timedelta(days=number_of_days_retro)
    # earliest_date = datetime(2020, 5, 21)
    max_number_of_nodes = 50 #Default 50

    import_flag = 1
    output_flag = 1
    
    if import_flag:
        #Check to see what data we have for the requested subreddit and consolidate it into a total file.
        if not os.path.exists(os.path.join(os.path.dirname(__file__),"dat")):
            print("Missing data folder! No data yet? : "+str(os.path.join(os.path.dirname(__file__)), "dat"))
            data_imported = 0
        else:
            if not os.path.exists(os.path.join(os.path.dirname(__file__), "dat", subreddit_request)):
                print("Missing data folder! No data yet? : "+str(os.path.join(os.path.dirname(__file__), "dat", subreddit_request)))
                data_imported = 0
            else:
                try:
                    [master_aux_path, master_post_path, master_comment_path] = consolidate_data_files(os.path.join(os.path.dirname(__file__),"dat", subreddit_request))
                    with open(master_aux_path,'rb') as file:
                        master_subreddit_info_dict = pickle.load(file)
                    with open(master_post_path,'rb') as file:
                        [master_node_list_post, master_node_colormap_list_post, master_node_labelmap_list_post, \
                        master_edge_list_post, master_edge_colormap_list_post] = pickle.load(file)
                    with open(master_comment_path,'rb') as file:
                        [master_node_list_comment, master_node_colormap_list_comment, master_node_labelmap_list_comment, \
                        master_edge_list_comment, master_edge_colormap_list_comment] = pickle.load(file)
                    data_imported = 1
                except FileNotFoundError:
                    print("Could not find data files...")
                    data_imported = 0
    else:
        data_imported = 0
    #No imported data? Go get some!
    if not data_imported:
        current_search_date = earliest_date
        while (current_search_date < yesterday_date):
            #For the post track
            subreddit_start_post = subreddit_request
            subreddit_count_post = 0
            subreddit_search_level_post = 1
            nodes_post = [subreddit_start_post.lower()]
            subreddits_remaining_post = [subreddit_start_post.lower()]

            edge_map_post = []
            edge_color_map_post = []

            node_color_map_post = []
            node_color_map_post.append(subreddit_search_level_post-1)
            node_label_map_post = dict()
            node_label_map_post[subreddit_count_post] = subreddit_start_post.lower()
            
            explored_subreddit_count_post = 0

            #For the comment track
            subreddit_start_comment = subreddit_request
            subreddit_count_comment = 0
            subreddit_search_level_comment = 1
            nodes_comment = [subreddit_start_comment.lower()]
            subreddits_remaining_comment = [subreddit_start_comment.lower()]

            edge_map_comment = []
            edge_color_map_comment = []

            node_color_map_comment = []
            node_color_map_comment.append(subreddit_search_level_comment-1)
            node_label_map_comment = dict()
            node_label_map_comment[subreddit_count_comment] = subreddit_start_comment.lower()
            
            explored_subreddit_count_comment = 0

            subreddit_info_dict = dict()
            post_finished = 0
            comment_finished = 0
            finished = 0
            while not finished:
                #Collect subreddit info first and then split paths
                temp_sub_combine = subreddits_remaining_post + subreddits_remaining_comment
                unique_sub_combine = list(set(temp_sub_combine))
                for unique_sub in unique_sub_combine:
                    if unique_sub not in subreddit_info_dict.keys():
                        print("Scraping info for r/"+str(unique_sub)+"...")
                        subreddit_info_dict[unique_sub] = dated_subreddit_query(unique_sub, current_search_date)

                #Traverse the posts first
                if not post_finished:
                    print("Starting next traversal level... (Reddit Level: Post-"+str(subreddit_search_level_post)+")...")
                    next_subreddits_post = subreddits_remaining_post.copy()
                    subreddits_remaining_post = []
                    for subreddit in next_subreddits_post:
                        if explored_subreddit_count_post >= max_number_of_nodes:
                            post_finished = 1
                            break
                        print("\tTraversing: r/"+str(subreddit)+" (Subreddit: "+str(explored_subreddit_count_post+1)+"/"+str(max_number_of_nodes)+")...")
                        sub_info = subreddit_info_dict[subreddit]
                        if sub_info == None:
                            print("\tNo info for r/"+subreddit+", something must have gone wrong...")
                            continue
                        nth_top = 1
                        retrieved_user_data = 0
                        while not retrieved_user_data and nth_top <= len(sub_info.posts):
                            top_poster_name = sub_info.dated_get_top_poster(current_search_date, n=nth_top)
                            print("\tCollecting User Post Info: u/"+top_poster_name+"...")
                            query_results = dated_user_query(top_poster_name, current_search_date)
                            if not query_results == None:
                                top_posters_posts = query_results[0]
                                top_posters_comments = query_results[1]
                                sub_connections = []
                                for post in top_posters_posts:
                                    if post.subreddit.lower() not in sub_connections and not post.subreddit.lower() == subreddit:
                                        sub_connections.append(post.subreddit.lower())
                                if sub_connections:
                                    retrieved_user_data = 1
                                    print("\t\tFound connections to...")
                                else:
                                    print("\t\tFound no connections.")
                            else:
                                print("\t\tInvalid user.")
                            nth_top = nth_top + 1
                        for connection in sub_connections:
                            print("\t\t\tr/"+connection)
                            if not connection in nodes_post:
                                subreddit_count_post = subreddit_count_post + 1
                                node_color_map_post.append(subreddit_search_level_post)
                                nodes_post.append(connection)
                                node_label_map_post[subreddit_count_post]=connection
                                if explored_subreddit_count_post < max_number_of_nodes:
                                    subreddits_remaining_post.append(connection)
                            edge_map_post.append([nodes_post.index(subreddit), nodes_post.index(connection)])
                            edge_color_map_post.append(subreddit_search_level_post)
                        explored_subreddit_count_post = explored_subreddit_count_post + 1
                    subreddit_search_level_post = subreddit_search_level_post + 1
                    if explored_subreddit_count_post >= max_number_of_nodes or not subreddits_remaining_post:
                        post_finished = 1

                #Then traverse the comment path
                if not comment_finished:
                    print("Starting next traversal level... (Reddit Level: Comment-"+str(subreddit_search_level_comment)+")...")
                    next_subreddits_comment = subreddits_remaining_comment.copy()
                    subreddits_remaining_comment = []
                    for subreddit in next_subreddits_comment:
                        if explored_subreddit_count_comment >= max_number_of_nodes:
                            comment_finished = 1
                            break
                        print("\tTraversing: r/"+str(subreddit)+" (Subreddit: "+str(explored_subreddit_count_comment+1)+"/"+str(max_number_of_nodes)+")...")
                        sub_info = subreddit_info_dict[subreddit]
                        if sub_info == None:
                            print("\tNo info for r/"+subreddit+", something must have gone wrong...")
                            continue
                        comment_num = len(sub_info.get_comments_as_list())
                        nth_top = 1
                        retrieved_user_data = 0
                        while not retrieved_user_data and nth_top <= comment_num:
                            top_commenter_name = sub_info.dated_get_top_commenter(current_search_date, n=nth_top)
                            print("\tCollecting User Comment Info: u/"+top_commenter_name+"...")
                            query_results = dated_user_query(top_commenter_name, current_search_date)
                            if not query_results == None:
                                top_commenter_posts = query_results[0]
                                top_commenter_comments = query_results[1]
                                sub_connections = []
                                for comment in top_commenter_comments:
                                    if comment.subreddit.lower() not in sub_connections and not comment.subreddit.lower() == subreddit:
                                        sub_connections.append(comment.subreddit.lower())
                                if sub_connections:
                                    retrieved_user_data = 1
                                    print("\t\tFound connections to...")
                                else:
                                    print("\t\tFound no connections.")
                            else:
                                print("\t\tInvalid user.")
                            nth_top = nth_top + 1
                        for connection in sub_connections:
                            print("\t\t\tr/"+connection)
                            if not connection in nodes_comment:
                                subreddit_count_comment = subreddit_count_comment + 1
                                node_color_map_comment.append(subreddit_search_level_comment)
                                nodes_comment.append(connection)
                                node_label_map_comment[subreddit_count_comment]=connection
                                if explored_subreddit_count_comment < max_number_of_nodes:
                                    subreddits_remaining_comment.append(connection)
                            edge_map_comment.append([nodes_comment.index(subreddit), nodes_comment.index(connection)])
                            edge_color_map_comment.append(subreddit_search_level_comment)
                        explored_subreddit_count_comment = explored_subreddit_count_comment + 1
                    subreddit_search_level_comment = subreddit_search_level_comment + 1
                    if explored_subreddit_count_comment >= max_number_of_nodes or not subreddits_remaining_comment:
                        comment_finished = 1
                finished = post_finished and comment_finished
            if output_flag:
                search_date_string = str(current_search_date.year)+"_"+str(current_search_date.day)+"_"+str(current_search_date.month)+"_"
                print("Outputting Reddit date for "+search_date_string+" starting at r/"+subreddit_request+"...")
                if not os.path.exists(os.path.dirname(__file__)+"/dat"):
                    os.mkdir(os.path.dirname(__file__)+"/dat")
                if not os.path.exists(os.path.dirname(__file__)+"/dat/"+subreddit_request):
                    os.mkdir(os.path.dirname(__file__)+"/dat/"+subreddit_request)
                auxilliary_file_name = search_date_string+subreddit_request+'.aux'
                post_plot_file_name = search_date_string+subreddit_request+'_post.plt'
                comment_plot_file_name = search_date_string+subreddit_request+'_comment.plt'
                with open(os.path.dirname(__file__)+"/dat/"+subreddit_request+"/"+auxilliary_file_name,'wb+') as file:
                    pickle.dump(subreddit_info_dict, file)
                with open(os.path.dirname(__file__)+"/dat/"+subreddit_request+"/"+post_plot_file_name,'wb+') as file:
                    pickle.dump([subreddit_start_post, subreddit_count_post, subreddit_search_level_post, nodes_post, subreddits_remaining_post,\
                        edge_map_post, edge_color_map_post, node_color_map_post, node_label_map_post, explored_subreddit_count_post], file)
                with open(os.path.dirname(__file__)+"/dat/"+subreddit_request+"/"+comment_plot_file_name,'wb+') as file:
                    pickle.dump([subreddit_start_comment, subreddit_count_comment, subreddit_search_level_comment, nodes_comment, subreddits_remaining_comment,\
                        edge_map_comment, edge_color_map_comment, node_color_map_comment, node_label_map_comment, explored_subreddit_count_comment], file)
                print("Consolidating gathered data so far...")
                try:
                    [master_aux_path, master_post_path, master_comment_path] = consolidate_data_files(os.path.join(os.path.dirname(__file__),"dat", subreddit_request))
                except FileNotFoundError:
                    print("Something went wrong consolidating files! Moving on though, please fix me before plotting!")
            current_search_date = current_search_date + timedelta(days=1)

#Now that we've got some data (generated or loaded), let's plot stuff!
#Gather data in the form of the consolidated master files for any scraping request
    if not data_imported:
        with open(master_aux_path,'rb') as file:
            master_subreddit_info_dict = pickle.load(file)
        with open(master_post_path,'rb') as file:
            [master_node_list_post, master_node_colormap_list_post, master_node_labelmap_list_post, \
            master_edge_list_post, master_edge_colormap_list_post] = pickle.load(file)
        with open(master_comment_path,'rb') as file:
            [master_node_list_comment, master_node_colormap_list_comment, master_node_labelmap_list_comment, \
            master_edge_list_comment, master_edge_colormap_list_comment] = pickle.load(file)

    labels_on = 0
    normal_plot = 0
    embedded_plot = 1

    movie_flag = 1
    if movie_flag:
        frames = []
    for t in range(len(master_node_list_post)):
        print("Now plotting for r/"+subreddit_request+" at time point: "+str(t))
        title = "Starting from r/"+subreddit_request+" at time point: "+str(t)
        plt.figure()
        if not labels_on:
            labels = None
        else:
            labels = master_node_labelmap_list_post[t]
        if normal_plot:
            regular_plot(title, master_edge_list_post[t], node_labels=labels,
                node_colors=master_node_colormap_list_post[t], edge_colors=master_edge_colormap_list_post[t],
                with_labels=labels_on)
        elif embedded_plot:
            plot_embed_graph(title, master_edge_list_post[t], node_labels=labels,
                node_colors=master_node_colormap_list_post[t], edge_colors=master_edge_colormap_list_post[t],
                with_labels=labels_on)
        if movie_flag:
            fig_name = subreddit_request+"_plot_"+str(t)+"_temp.png"
            plt.savefig(os.path.join(os.path.dirname(__file__),"dat", subreddit_request, fig_name))
            frames.append(os.path.join(os.path.dirname(__file__),"dat", subreddit_request, fig_name))
        plt.show()
    for frame in frames:
        os.remove(frame)
    