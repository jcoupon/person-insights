#!/usr/bin/env python

"""
Jean coupon - 2018
scripts to clean NOTAMs, train, test 
and predict NOTAMS groups and importance
"""

import numpy as np
import os
import sys
import re
import pandas as pd
import pickle

# add ./python to python path
#sys.path.insert(0, '../python')

# load local libraries
import cleaning
import modelling

#import text_processing

"""

-------------------------------------------------------------
global variables
-------------------------------------------------------------

"""


"""

-------------------------------------------------------------
main
-------------------------------------------------------------

"""


def main(args):
    """ Main function
    """

    path_in = args.path_in

    # output file path
    if args.path_out is None:
        # keep the path basename (without the extension)
        try:
            path_out, file_extension = os.path.splitext(path_in)
        except:
            # if the input file has no extension
            # keep it as is
            path_out = path_in
    
    if args.task == 'clean':
        clean(
            path_in, 
            path_out+'_clean.csv' if args.path_out is None else args.path_out,
            )

        return

    if args.task == 'train':

        if args.path_model is None:
            path_model = path_out+'_model_vectorize.pickle'
            path_model += ','+path_out+'_model_cluster.pickle'
        else:
            path_model = args.path_model            

        train(
            path_in,
            path_model,
            args.n_dim,
            vectorize_method=args.vectorize_method,
            cluster_method=args.cluster_method,
            )

        return

    if args.task == 'train_classifier':

        if args.path_model is None:
            path_model = path_out+'_model_classifier.pickle'
        else:
            path_model = args.path_model            

        train_classifier(
            path_in,
            path_model,
            )

        return



    if args.task == 'predict':

        if args.path_model is None:
            path_model = path_out+'_model_vectorize.pickle'
            path_model += ','+path_out+'_model_cluster.pickle'
        else:
            path_model = args.path_model            

        predict(
            path_in,
            path_out+'_predict.csv' if args.path_out is None else args.path_out,
            path_model,
            args.cluster_dist,
            vectorize_method=args.vectorize_method,
            cluster_method=args.cluster_method,
            tSNE=args.tSNE,
            )

        return

    if args.task == 'predict_classifier':

        if args.path_model is None:
            path_model = path_out+'_model_classifier.pickle'
        else:
            path_model = args.path_model            

        predict_classifier(
            path_in,
            path_out+'_predict_class.csv' if args.path_out is None else args.path_out,
            path_model,
            )

        return

    raise Exception('task {} not recognized. Run main.py --help for details.'.format(args.task))


"""

-------------------------------------------------------------
Main functions
-------------------------------------------------------------


"""

def clean(path_in, path_out):
    """Read NOTAM csv file, perform cleaning
    and write into new csv file.
    """
    
    sys.stdout.write('Task: clean.\n\nOutput file path:{0}\n\n'.format(path_out)); sys.stdout.flush()

    # create cleaner object and read the data
    cleaner = cleaning.Cleaning(path=path_in, sep=args.sep)

    # split the NOTAM into items (Q, A, B, C, etc.) 
    cleaner.split()

    # clean the unstructured (E) part
    cleaner.clean()

    # write result
    cleaner.write(path_out)

    return

def train(
        path_in, path_model, n_dim, 
        vectorize_method='word2vec', 
        cluster_method='hierarch_cosine_average'):
    """Read clean NOTAM csv file, train vectorize and 
    clustering (unsupervised) models and write model files.
    """

    # define the paths out for the models
    try:
        path_out_vectorize,path_out_cluster = path_model.split(',')
    except:
        raise Exception('train(): please provide 2 output paths separated by a coma (path_out_vectorize,path_out_cluster).')
    
    sys.stdout.write(
        'Task: train.\n\nOutput model paths:\nvectorize:{0}\ncluster:{1}\n\n'.format(
            path_out_vectorize, path_out_cluster)); sys.stdout.flush()

    # create training object
    model_train = modelling.ModelTraining(path_in)

    # vectorize the NOTAMs and do
    # dimensionality reduction
    model_train.vectorize(
        path_out=path_out_vectorize, 
        method=vectorize_method, 
        n_dim=n_dim,
        )

    # train and persist model
    if cluster_method == 'hierarch_cosine_average':
        method = 'hierarchical'
        method_options_dict = {'method': 'average', 'metric': 'cosine'}

    if cluster_method == 'hierarch_euclid_ward':
        method = 'hierarchical'
        method_options_dict = {'method': 'ward'}

    model_train.cluster_train(
        path_out=path_out_cluster, 
        method=method,
        method_options_dict=method_options_dict,
        )

    return

def train_classifier(
        path_in, path_model,
    ):
    """Read clean NOTAM csv file, train vectorize and 
    clustering (unsupervised) models and write model files.
    """
    
    sys.stdout.write(
        'Task: train_classifier.\n\nOutput model path cluster:{0}\n\n'.format(
            path_model)); sys.stdout.flush()

    # create training object
    model_train = modelling.ModelTraining(path_in)

    model_train.class_train(
        path_out=path_model,
        )

    return


def predict(
        path_in, path_out, path_model, cluster_dist, 
        vectorize_method='word2vec', 
        cluster_method='hierarch_cosine_average',
        tSNE=False,
        ):
    """Read clean NOTAM csv file, read model files and
    clustering (unsupervised) models, and do clustering.
    """

    # get the paths out for the models
    try:
        path_in_vectorize,path_in_cluster = path_model.split(',')
    except:
        raise Exception('predict(): please provide 2 output paths separated by a coma (path_out_vectorize,path_out_cluster).')

    sys.stdout.write(
        'Task: predict.\n\nInput model paths:\nvectorize:{0}\ncluster:{1}\n\n'.format(
            path_in_vectorize, path_in_cluster)); sys.stdout.flush()

    # create predict object
    model_predict = modelling.ModelPredict(path_in)

    # vectorize the NOTAMs and do
    # dimensionality reduction
    model_predict.vectorize(
        path_in=path_in_vectorize,
        method=vectorize_method,
        )

    if cluster_dist == 'test':
        # loop over different values of 
        # cluster distances and record the 
        # number of clusters with a purity
        # higher than 80%.
        # write purity values and exit

        n_clusters, dist, f_pure = model_predict.cluster_test(
            path_in = path_in_cluster,
        )

        pd.DataFrame.from_dict({
            'n_clusters': n_clusters, 
            'dist': dist,
            'f_pure': f_pure}).to_csv(path_out, index=False)

        return

    if cluster_dist == 'guess':
        # find the value that gives a 
        # reasonable number of clusters 
        with open(path_in_cluster, 'rb') as file_in:
            _, _, Z = pickle.load(file_in)

        cluster_dist = np.quantile(Z[:,2], 0.995)
    else:

        cluster_dist = float(cluster_dist)

    model_predict.cluster_predict(
        path_in = path_in_cluster,
        dist = cluster_dist,
    )

    # TODO: add random state
    if tSNE:
        model_predict.visualize(method='t-SNE')

    # write result
    model_predict.write(path_out)

    return



def predict_classifier(
        path_in, path_out, path_model,
        ):
    """Read clean NOTAM csv file with word vectors, read model files and 
    does classification models.
    """

    sys.stdout.write(
        'Task: predict_classifier.\n\n\
Input model path:{0}\n\n'.format(path_model)); sys.stdout.flush()

    # create predict object
    model_predict = modelling.ModelPredict(path_in)

    model_predict.class_predict(
        path_in = path_model,
    )

    # write result
    model_predict.write(path_out)

    return



def plot_test(
        path_in, path_out):
    """Read NOTAM csv file that contains 
    both important class and cluster labels.
    """

    # create test object
    model_test = modelling.ModelTest(path_in)



    return



"""

-------------------------------------------------------------
Utils
-------------------------------------------------------------


"""


"""

-------------------------------------------------------------
Main call and arguments
-------------------------------------------------------------


"""

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        'task',
        help='Task to perform among \'clean\',\'train\', ,\'train_classifier\', \'predict\' and \'predict_classifier\'',
    )

    parser.add_argument(
        'path_in', default=None,
        help='Input file path (csv file with NOTAMs)')

    parser.add_argument(
        '-path_out', default=None,
        help='Output file path. Write a file with cleaned NOTAMs for \'clean\', \
or \'predict\' output (group and importance) depending on the task. \
Default: path based on input file path with task name appended to the name.')

    parser.add_argument(
        '-path_model', default=None,
        help='Output model file path (output for \'train\' and \
input for \'predict\'). Please provide 2 file names separated \
by a coma, first providing a path for the vectorizing model, \
then for the cluster model, e.g: model_vectorize.pickle,model_cluster.pickle')

    parser.add_argument(
        '-seed', default=None, type=int, help='Random seed.')

    parser.add_argument(
        '-sep', default=',', help='Separator for the input file.')

    parser.add_argument(
        '-vectorize_method', default='word2vec', 
        help='Method to vectorize the NOTAMs. Default: TFIDF-SVD.')

    parser.add_argument(
        '-n_dim', type=int, default=50, 
        help='Dimension of the vector. Default: 50')

    parser.add_argument(
        '-cluster_method', default='hierarch_cosine_average', 
        help='Metric to cluster the NOTAMs. Default: hierarch_cosine_average.')

    parser.add_argument(
        '-cluster_dist', default='guess', 
        help='Used in \'predict\' only: distance to select the clusters when \
trained with hierarchical clustering. Takes a float value, or \'guess\' \
(based in the quantiles of the linkage matrix to give roughly 50 clusters)\
, or \'test\' (used only for testing purpose: will compute the cluster purity \
for a number of clusters and output result in path_out).')

    parser.add_argument(
        '-tSNE', action='store_true', 
        help='Perform t-SNE manifold.')

    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(seed=args.seed)

    main(args)
