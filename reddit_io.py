import os

import pickle

import datetime

from reddit_extrapolate import *

def consolidate_data_files(path_to_data):
    path_to_parent, sub_request = os.path.split(path_to_data)
    aux_files = []
    post_plot_files = []
    comment_plot_files = []
    for file in os.listdir(path_to_data):
        file_path = os.path.join(path_to_data, file)
        # print(file_path)
        if not "master" in file:
            if file.endswith(".aux"):
                aux_files.append(file_path)
            elif file.endswith(".plt"):
                if "comment.plt" in file_path:
                    comment_plot_files.append(file_path)
                elif "post.plt" in file_path:
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
    max_aux_path = os.path.join(path_to_data, "master_"+sub_request+".aux")
    if not os.path.exists(max_aux_path):  
        master_sub_dict = dict()
    else:
        with open(max_aux_path, 'rb') as file:
            master_sub_dict = pickle.load(file)
    for aux_file in aux_files:
        with open(aux_file, 'rb') as file:
            sub_info_structure = pickle.load(file)
        for subreddit in sub_info_structure.keys():
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
    max_post_path = os.path.join(path_to_data, "master_"+sub_request+"_post.plt")
    max_comment_path = os.path.join(path_to_data, "master_"+sub_request+"_comment.plt")
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

if __name__ == "__main__":
    subreddit_request = "AskReddit"
    consolidate_data_files(os.path.join(os.path.dirname(__file__),"dat", subreddit_request))
