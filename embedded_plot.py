from gem.evaluation import visualize_embedding as viz
from gem.evaluation import evaluate_graph_reconstruction as gr
from time import time

from gem.embedding.hope     import HOPE
from gem.embedding.lap      import LaplacianEigenmaps
from gem.embedding.lle      import LocallyLinearEmbedding

import networkx as nx
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from math import log10

from reddit_scrape import get_popularity


def weight_edges(edge_map, b_normalize):
    normalize_scale = 1
    weighted_map = []
    explored_edges = []
    max_frequency = 0
    total_e = len(edge_map)
    coun = 0
    for edge in edge_map:
        edge_frequency = 0
        if (coun % 1000 == 0):
            print("Edge "+str(coun)+"/"+str(total_e))
        if not edge in explored_edges:
            for other_edge in edge_map:
                if(other_edge == edge):
                    edge_frequency = edge_frequency + 1
            weighted_map.append([edge[0], edge[1], edge_frequency])
            if edge_frequency > max_frequency:
                max_frequency = edge_frequency
            explored_edges.append(edge)
        coun = coun + 1
    if(b_normalize):
        #By this point we should have only unique edges with an additional frequency count, now normalize them
        explored_edges = weighted_map.copy()
        weighted_map = []
        for edge_with_freq in explored_edges:
            weighted_map.append([edge_with_freq[0], edge_with_freq[1], (edge_with_freq[2]/float(max_frequency))*normalize_scale])
    return weighted_map

def colorize_nodes(label_dictionary):
    colors = []
    sub_count = 0
    num_subs = len(label_dictionary.keys())
    for label in label_dictionary.keys():
        subreddit_name = label_dictionary[sub_count]
        sub_pop = get_popularity(subreddit_name)
        try:
            colors.append(log10(sub_pop))
        except ValueError:
            colors.append(0)
        print("("+str(sub_count)+"/"+str(num_subs)+") r/"+subreddit_name+" has "+str(sub_pop)+" subs...")
        sub_count = sub_count + 1
    return colors

def plot_embed_graph(subreddit_title, graph_edges_weighted, graph_labels=None, skip_training=0, sub_colors=None):
    plot_HOPE = 1
    plot_LE = 1
    plot_LLE = 0
    # Construct Graph or DiGraph from data collected. 
    G = nx.DiGraph()
    print("Adding edges...")
    for edge in graph_edges_weighted:
        G.add_edge(edge[0], edge[1], weight=edge[2])

    models = []
    if(plot_HOPE):
        # HOPE takes embedding dimension (d) and decay factor (beta) as inputs
        models.append(HOPE(d=4, beta=0.01))
    if(plot_LE):
        # LE takes embedding dimension (d) as input
        models.append(LaplacianEigenmaps(d=2))
    if(plot_LLE):
        # LLE takes embedding dimension (d) as input
        models.append(LocallyLinearEmbedding(d=2))

    model_count = 0
    for embedding in models:
        model_count = model_count + 1
        plt.figure(model_count)
        print ('Num nodes: %d, num edges: %d' % (G.number_of_nodes(), G.number_of_edges()))
        if not skip_training:
            t1 = time()
            # Learn embedding - accepts a networkx graph or file with edge list
            print("Now we train...")
            Y, t = embedding.learn_embedding(graph=G, edge_f=None, is_weighted=True, no_python=True)
            print (embedding._method_name+':\n\tTraining time: %f' % (time() - t1))
            # Evaluate on graph reconstruction
            # MAP, prec_curv, err, err_baseline = gr.evaluateStaticGraphReconstruction(G, embedding, Y, None)
            #---------------------------------------------------------------------------------
            # print(("\tMAP: {} \t precision curve: {}\n\n\n\n"+'-'*100).format(MAP,prec_curv[:5]))
        #---------------------------------------------------------------------------------
        # Visualize
        print("Training finished... Let's visualize...")
        viz.plot_embedding2D(embedding.get_embedding(), di_graph=G, node_colors=sub_colors, labels=graph_labels)
        plt.title("Scraping Reddit starting from "+subreddit_title)
        plt.show()

if __name__ == "__main__":
    edges = [[0, 31],[0, 21],[0, 19],[0, 17],[0, 13],[0, 12],[0, 11],[0, 10],[0, 8],[0, 7],[0, 6],[0, 5],[0, 4],[0, 3],[0, 2],[0, 1],[1, 30],[1, 21],[1, 19],[1, 17],[1, 13],[1, 7],[1, 3],[1, 2],[2, 13],[2, 8],[2, 9],[2, 32],[2, 28],[2, 27],[2, 7],[2, 3],[3, 13],[3, 12],[3, 7],[4, 10],[4, 6],[5, 16],[5, 10],[5, 6],[6, 16],[8, 33],[8, 32],[8, 32],[9, 33],[13, 33], [14, 33], [14, 32], [15, 33], [15, 32], [18, 33], [18, 32], [19, 33], [20, 33], [20, 32], [22, 33], [22, 32], [23, 29], [23, 33], [23, 32], [23, 27], [23, 25], [24, 31], [24, 27], [24, 25], [25, 31], [26, 33], [26, 29], [27, 33], [28, 33], [28, 31], [29, 33], [29, 32], [30, 33], [30, 32], [31, 33], [31, 32], [32, 33]] 
    labelz = {0:'Zero',1:'One',2:'Two',3:'Three',4:'Four',5:'Five',6:'Six',7:'Seven',8:'Eight',9:'Nine',10:'Ten',11:'Eleven',12:'Twelve',13:'Thirteen',14:'Fourteen',15:'Fifteen',16:'Sixteen',17:'Seventeen',18:'Eighteen',19:'Nineteen',20:'Twenty',21:'Twenty-One',22:'Twenty-Two',23:'Twenty-Three',24:'Twenty-Four',25:'Twenty-Five',26:'Twenty-Six',27:'Twenty-Seven',28:'Twenty-Eight',29:'Twenty-Nine',30:'Thirty',31:'Thirty-One',32:'Thirty-Two',33:'Thirty-Three'}
    plot_embed_graph(edges, labelz)