
from time import time
import networkx as nx
import pickle
import numpy as np
import os

#import helper libraries
from dynamicgem.utils      import graph_util, plot_util, dataprep_util
from dynamicgem.evaluation import visualize_embedding as viz
from dynamicgem.visualization import plot_dynamic_sbm_embedding
from dynamicgem.evaluation import evaluate_graph_reconstruction as gr
from dynamicgem.graph_generation import dynamic_SBM_graph as sbm

#import the methods
from dynamicgem.embedding.ae_static    import AE
from dynamicgem.embedding.dynamicTriad import dynamicTriad
from dynamicgem.embedding.TIMERS       import TIMERS
from dynamicgem.embedding.dynAE        import DynAE
from dynamicgem.embedding.dynRNN       import DynRNN
from dynamicgem.embedding.dynAERNN     import DynAERNN

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

def plot_dynam_graph(title, graph_list):
    #dynAERNN
    graphs = graph_list
    dynamic_sbm_series = graphs
    outdir = os.path.exists(os.path.dirname(__file__)+"/out")
    testDataType = 'sbm_cd'
    length = 7
    dim_emb  = 128
    lookback = 2
    embedding = DynAERNN(d   = dim_emb,
                beta           = 5,
                n_prev_graphs  = lookback,
                nu1            = 1e-6,
                nu2            = 1e-6,
                n_aeunits      = [500, 300],
                n_lstmunits    = [500,dim_emb],
                rho            = 0.3,
                n_iter         = 250,
                xeta           = 1e-3,
                n_batch        = 100,
                modelfile      = ['./intermediate/enc_model_dynAERNN.json', 
                                './intermediate/dec_model_dynAERNN.json'],
                weightfile     = ['./intermediate/enc_weights_dynAERNN.hdf5', 
                                './intermediate/dec_weights_dynAERNN.hdf5'],
                savefilesuffix = "testing")

    embs = []
    t1 = time()
    for temp_var in range(lookback+1, length+1):
                    emb, _ = embedding.learn_embeddings(graphs[:temp_var])
                    embs.append(emb)
    print (embedding._method_name+':\n\tTraining time: %f' % (time() - t1))
    plt.figure()
    plt.clf()    
    plot_dynamic_sbm_embedding.plot_dynamic_sbm_embedding_v2(embs[-5:-1], dynamic_sbm_series[-5:])    
    plt.show()

    #dynamicTriad
    datafile  = dataprep_util.prep_input_dynTriad(graphs, length, testDataType)
    embedding= dynamicTriad(niters     = 20,
                    starttime  = 0,
                    datafile   = datafile,
                    batchsize  = 1000,
                    nsteps     = length,
                    embdim     = dim_emb,
                    stepsize   = 1,
                    stepstride = 1,
                    outdir     = outdir,
                    cachefn    = '/tmp/'+ testDataType,
                    lr         = 0.1,
                    beta       = [0.1,0.1],
                    negdup     = 1,
                    datasetmod = 'core.dataset.adjlist',
                    trainmod   = 'dynamicgem.dynamictriad.core.algorithm.dynamic_triad',
                    pretrain_size = length,
                    sampling_args = {},
                    validation = 'link_reconstruction',
                    datatype   = testDataType,
                    scale      = 1,
                    classifier = 'lr',
                    debug      = False,
                    test       = 'link_predict',
                    repeat     = 1,
                    resultdir  = outdir,
                    testDataType = testDataType,
                    clname       = 'lr')
                    #node_num     = node_num )
    t1 = time()
    embedding.learn_embedding()
    print (embedding._method_name+':\n\tTraining time: %f' % (time() - t1))
    embedding.get_embedding()
    embedding.plotresults(dynamic_sbm_series)