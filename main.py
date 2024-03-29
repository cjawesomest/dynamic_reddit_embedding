import pickle
import os.path

from datetime import datetime, timedelta
from reddit_scrape import *
from local_io import *
from embedded_plot import *
# from embedded_dynamic import *

import os
import sys
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np

# REQUIRED_ARGS = ["request", "sub_limit", "end_date", "start_date", "lookback_days",
#     "import", "export", "export_dir"]
EXAMPLE_ARGS_PATH = "./config_examples.json"

def parse_args_json(example_name: str = "Example 1", 
        json_arg_path: str = EXAMPLE_ARGS_PATH):
    with open(json_arg_path) as json_file:
        data = json.load(json_file)
    return data[example_name]


if __name__ == "__main__":
    # Load default arguments
    defaults = parse_args_json()
    parser = argparse.ArgumentParser(description="Parsing arguments...")
    for key in defaults.keys():
        parser.add_argument('--'+key, default=defaults[key])
    args = parser.parse_args()

    # Assign values as necessary
    subreddit_request = args.request
    if args.end_date == "Today":
        today_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        yesterday_date = today_date - timedelta(days=1)
    number_of_days_retro = args.lookback_days
    if args.start_date == "Lookback":
        earliest_date = yesterday_date - timedelta(days=number_of_days_retro)
    # earliest_date = datetime(2020, 5, 21)
    max_number_of_nodes = args.sub_limit

    import_flag = args.import_flag
    output_flag = args.export_flag
    
    if import_flag:
        data_package = pickle_load(subreddit_request)
        #TODO: Convenient class for all this gunk
        master_subreddit_info_dict, master_node_list_post, master_node_colormap_list_post, master_node_labelmap_list_post, \
                    master_edge_list_post, master_edge_colormap_list_post, master_node_list_comment, master_node_colormap_list_comment, master_node_labelmap_list_comment, \
                    master_edge_list_comment, master_edge_colormap_list_comment = data_package
    else:
        data_package = 0
    #No imported data? Go get some!
    if not data_package == None:
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
                #TODO: Convenient class for all this gunk; Add customizable save location
                [master_aux_path, master_post_path, master_comment_path] = pickle_save(data = [subreddit_info_dict, subreddit_start_post, subreddit_count_post, subreddit_search_level_post, nodes_post, subreddits_remaining_post,\
                        edge_map_post, edge_color_map_post, node_color_map_post, node_label_map_post, explored_subreddit_count_post, subreddit_start_comment, subreddit_count_comment, subreddit_search_level_comment, nodes_comment, subreddits_remaining_comment,\
                        edge_map_comment, edge_color_map_comment, node_color_map_comment, node_label_map_comment, explored_subreddit_count_comment],
                    subreddit=subreddit_request,
                    date = current_search_date)
            current_search_date = current_search_date + timedelta(days=1)

#TODO: Put this plotting stuff into it's own set of functions
#Now that we've got some data (generated or loaded), let's plot stuff!
#Gather data in the form of the consolidated master files for any scraping request
    if not data_package == None:
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
    embedded_plot = 0
    dynamic_plot = 0
    display_plots = 1
    graph_list = []

    movie_flag = 1
    if movie_flag:
        frames = []
    if not dynamic_plot:
        for t in range(len(master_node_list_post)):
            print("Now plotting for r/"+subreddit_request+" at time point: "+str(t))
            title = "Starting from r/"+subreddit_request+" at time point: "+str(t)
            plt.figure()
            if not labels_on:
                labels = None
            else:
                labels = master_node_labelmap_list_post[t]
            if not master_edge_colormap_list_post[t]:
                print("There are no edges here? Strange. Moving on...")
                continue
            this_graph = None
            if normal_plot:
                this_graph = regular_plot(title, master_edge_list_post[t], node_labels=labels,
                    node_colors=master_node_colormap_list_post[t], edge_colors=master_edge_colormap_list_post[t],
                    with_labels=labels_on)
            #DOES NOT WORK
            elif embedded_plot:
                this_graph = plot_embed_graph(title, master_edge_list_post[t], node_labels=labels,
                    node_colors=master_node_colormap_list_post[t], edge_colors=master_edge_colormap_list_post[t],
                    with_labels=labels_on)
            if movie_flag:
                fig_name = subreddit_request+"_plot_"+str(t)+"_temp.png"
                plt.savefig(os.path.join(os.path.dirname(__file__),"dat", subreddit_request, fig_name))
                frames.append(os.path.join(os.path.dirname(__file__),"dat", subreddit_request, fig_name))
            if display_plots:
                plt.show()
            graph_list.append(this_graph)
        for frame in frames:
            os.remove(frame)
        with open(os.path.join(os.path.dirname(__file__),"dat", subreddit_request, "graph_list.grph"), 'wb+') as file:
            pickle.dump(graph_list, file)
    else:
        #Dynamic embedding doesn't work with graph set, still working on issue
        pass
        # with open(os.path.join(os.path.dirname(__file__),"dat", subreddit_request, "graph_list.grph"), 'rb') as file:
        #     graph_list = pickle.load(file)
        # plot_dynam_graph("Starting from r/"+subreddit_request+": Plotting Dynamic Change", graph_list)
        # if display_plots:
        #     plt.show()

    
