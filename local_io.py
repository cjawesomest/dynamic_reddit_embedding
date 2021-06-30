# CJ
# Utilities for storing and reading scraped information on a local filesystem

import os
import pickle
import datetime
from reddit_extrapolate import *

PICKLE_FILE_EXTENSION = '.aux'
PLOT_FILE_EXTENSION = '.plt'
DATA_DIRECTORY = 'dat'

#TODO: Give this a description and make it faster
def consolidate_pickle_files(path_to_data):
    path_to_parent, sub_request = os.path.split(path_to_data)
    aux_files = []
    post_plot_files = []
    comment_plot_files = []
    for file in os.listdir(path_to_data):
        file_path = os.path.join(path_to_data, file)
        # print(file_path)
        if not "master" in file:
            if file.endswith(PICKLE_FILE_EXTENSION):
                aux_files.append(file_path)
            elif file.endswith(PLOT_FILE_EXTENSION):
                if ("comment"+PLOT_FILE_EXTENSION) in file_path:
                    comment_plot_files.append(file_path)
                elif ("post"+PLOT_FILE_EXTENSION) in file_path:
                    post_plot_files.append(file_path)
                else:
                    continue
            else:
                continue
        else:
            continue
    #First consolidate all auxiliary data generated
    earliest_date = datetime.now()
    latest_date = datetime(1997, 11, 19)
    max_aux_path = os.path.join(path_to_data, "master_"+sub_request+PICKLE_FILE_EXTENSION)
    if not os.path.exists(max_aux_path):  
        master_sub_dict = dict()
    else:
        with open(max_aux_path, 'rb') as file:
            master_sub_dict = pickle.load(file)
    for aux_file in aux_files:
        with open(aux_file, 'rb') as file:
            sub_info_structure = pickle.load(file)
        for subreddit in sub_info_structure.keys():
            if not sub_info_structure[subreddit]:
                continue
            if sub_info_structure[subreddit].posts:
                this_date = sub_info_structure[subreddit].posts[0].date
            if this_date < earliest_date:
                earliest_date = datetime(this_date.year, this_date.month, this_date.day)
            if latest_date < this_date:
                latest_date = datetime(this_date.year, this_date.month, this_date.day)
            if subreddit not in master_sub_dict.keys():
                master_sub_dict[subreddit] = sub_info_structure[subreddit]
            else:
                master_sub_dict[subreddit].add_update_posts(sub_info_structure[subreddit].posts)
    with open(max_aux_path, "wb+") as file:
        pickle.dump(master_sub_dict, file)

    total_days = (latest_date - earliest_date).days
    total_indices = total_days + 1
    #Then create some multi-dimensional lists for the comment and post graph properties
    max_post_path = os.path.join(path_to_data, "master_"+sub_request+"_post"+PLOT_FILE_EXTENSION)
    max_comment_path = os.path.join(path_to_data, "master_"+sub_request+"_comment"+PLOT_FILE_EXTENSION)
    for max_plot_path in [max_post_path, max_comment_path]:
        if not os.path.exists(max_plot_path):  
            master_node_list = [[] for x in range(total_indices)]
            master_node_colormap_list = [[] for x in range(total_indices)]
            master_node_labelmap_list = [[] for x in range(total_indices)]

            master_edge_list = [[] for x in range(total_indices)]
            master_edge_colormap_list = [[] for x in range(total_indices)]
        else:
            with open(max_plot_path, 'rb') as file:
                [master_node_list, master_node_colormap_list, master_node_labelmap_list, \
                master_edge_list, master_edge_colormap_list] = pickle.load(file)
            #New Date info has been added
            if total_indices > len(master_node_list):
                while len(master_node_list) < total_indices:
                    master_node_list.append([])
                    master_node_colormap_list.append([])
                    master_node_labelmap_list.append([])
                    master_edge_list.append([])
                    master_edge_colormap_list.append([])
        if max_plot_path == max_post_path:
            post_or_comment_plot_files = post_plot_files
        elif max_plot_path == max_comment_path:
            post_or_comment_plot_files = comment_plot_files
        for plot_file in post_or_comment_plot_files:
            path_to_parent, post_filename = os.path.split(plot_file)
            split_name = post_filename.split("_")
            this_date = datetime(int(split_name[0]), int(split_name[2]), int(split_name[1]))
            date_index = (this_date - earliest_date).days
            with open(plot_file, 'rb') as file:
                [this_start, this_count, this_search_level, this_node_list, \
                this_subs_remaining, this_edge_map, this_edge_colormap, \
                this_node_colormap, this_node_labelmap, this_explored_count] = pickle.load(file)
            master_node_list[date_index] = this_node_list
            master_node_colormap_list[date_index] = this_node_colormap
            master_node_labelmap_list[date_index] = this_node_labelmap
            master_edge_list[date_index] = this_edge_map
            master_edge_colormap_list[date_index] = this_edge_colormap
        with open(max_plot_path, "wb+") as file:
            pickle.dump([master_node_list, master_node_colormap_list, master_node_labelmap_list, \
            master_edge_list, master_edge_colormap_list], file)
    return [max_aux_path, max_post_path, max_comment_path]

def pickle_load(subreddit_request: str, data_directory: str = DATA_DIRECTORY):
    #Check to see what data we have for the requested subreddit and consolidate it into a total file.
    print("Now importing and consolidating data files...")
    if not os.path.exists(os.path.join(os.path.dirname(__file__),data_directory)):
        print("Missing data folder! No data yet? : "+str(os.path.join(os.path.dirname(__file__)), data_directory))
        return None
    else:
        if not os.path.exists(os.path.join(os.path.dirname(__file__), data_directory, subreddit_request)):
            print("Missing data folder! No data yet? : "+str(os.path.join(os.path.dirname(__file__), data_directory, subreddit_request)))
            return None
        else:
            try:
                [master_aux_path, master_post_path, master_comment_path] = consolidate_pickle_files(os.path.join(os.path.dirname(__file__), data_directory, subreddit_request))
                with open(master_aux_path,'rb') as file:
                    master_subreddit_info_dict = pickle.load(file)
                with open(master_post_path,'rb') as file:
                    [master_node_list_post, master_node_colormap_list_post, master_node_labelmap_list_post, \
                    master_edge_list_post, master_edge_colormap_list_post] = pickle.load(file)
                with open(master_comment_path,'rb') as file:
                    [master_node_list_comment, master_node_colormap_list_comment, master_node_labelmap_list_comment, \
                    master_edge_list_comment, master_edge_colormap_list_comment] = pickle.load(file)
                #TODO: Pack all this data into a convenient class
                return [master_subreddit_info_dict, master_node_list_post, master_node_colormap_list_post, master_node_labelmap_list_post, \
                    master_edge_list_post, master_edge_colormap_list_post, master_node_list_comment, master_node_colormap_list_comment, master_node_labelmap_list_comment, \
                    master_edge_list_comment, master_edge_colormap_list_comment]
            except FileNotFoundError:
                print("Could not find data files...")
                return None

#TODO: Implement that convenient data wrapping class instead of generic 'data' array
def pickle_save(data, subreddit: str, date: datetime):
    [subreddit_info_dict, subreddit_start_post, subreddit_count_post, subreddit_search_level_post, nodes_post, subreddits_remaining_post,\
            edge_map_post, edge_color_map_post, node_color_map_post, node_label_map_post, explored_subreddit_count_post, subreddit_start_comment, subreddit_count_comment, subreddit_search_level_comment, nodes_comment, subreddits_remaining_comment,\
            edge_map_comment, edge_color_map_comment, node_color_map_comment, node_label_map_comment, explored_subreddit_count_comment] = data
    search_date_string = str(date.year)+"_"+str(date.day)+"_"+str(date.month)+"_"
    print("Outputting Reddit date for "+search_date_string+" starting at r/"+subreddit+"...")
    if not os.path.exists(os.path.dirname(__file__)+"/dat"):
        os.mkdir(os.path.dirname(__file__)+"/dat")
    if not os.path.exists(os.path.dirname(__file__)+"/dat/"+subreddit):
        os.mkdir(os.path.dirname(__file__)+"/dat/"+subreddit)
    auxilliary_file_name = search_date_string+subreddit+'.aux'
    post_plot_file_name = search_date_string+subreddit+'_post.plt'
    comment_plot_file_name = search_date_string+subreddit+'_comment.plt'
    with open(os.path.dirname(__file__)+"/dat/"+subreddit+"/"+auxilliary_file_name,'wb+') as file:
        pickle.dump(subreddit_info_dict, file)
    with open(os.path.dirname(__file__)+"/dat/"+subreddit+"/"+post_plot_file_name,'wb+') as file:
        pickle.dump([subreddit_start_post, subreddit_count_post, subreddit_search_level_post, nodes_post, subreddits_remaining_post,\
            edge_map_post, edge_color_map_post, node_color_map_post, node_label_map_post, explored_subreddit_count_post], file)
    with open(os.path.dirname(__file__)+"/dat/"+subreddit+"/"+comment_plot_file_name,'wb+') as file:
        pickle.dump([subreddit_start_comment, subreddit_count_comment, subreddit_search_level_comment, nodes_comment, subreddits_remaining_comment,\
            edge_map_comment, edge_color_map_comment, node_color_map_comment, node_label_map_comment, explored_subreddit_count_comment], file)
    print("Consolidating gathered data so far...")
    try:
        [master_aux_path, master_post_path, master_comment_path] = consolidate_pickle_files(os.path.join(os.path.dirname(__file__),"dat", subreddit))
        return [master_aux_path, master_post_path, master_comment_path]
    except FileNotFoundError:
        print("Something went wrong consolidating files! Moving on though, please fix me before plotting!")

if __name__ == "__main__":
    start = "AskReddit"
    consolidate_pickle_files(os.path.join(os.path.dirname(__file__), DATA_DIRECTORY, start))