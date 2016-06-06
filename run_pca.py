import json, os, csv, ast, sys, math, re
import numpy as np
import matplotlib.pyplot as plt
from operator import itemgetter
from cluster import *

##########################################
# TODO:
#  * Clean this code up
#  * variablize this stuff (get rid of magic numbers)
#  * calculate % variance
#  * visualize clusters (using top 2 thingies)


def distanceMetric(a, b):
    # euc distance between a and b
    return math.sqrt(sum([ (a["data"][i] - b["data"][i])**2 for i in range(0, len(a["data"])) ]))

def calcCentroid(bucket):
    cen_vals = []
    for i in range(0, len(bucket[0]["data"])):
        total = 0
        for member in bucket:
            total += member["data"][i]
        cen_vals.append(total / float(len(bucket)))
    return {"data": cen_vals, "label": "centroid"}


if __name__ == "__main__":
    settings_fp = "param/settings.json"
    FORCE_GEN_EIGEN_VECTORS = False
    # Load up the settings
    with open(settings_fp) as fp:
        settings = json.load(fp)
    metrics_dump = settings["analysis"]["metrics_dump"]
    world_width = settings["analysis"]["world_width"]

    # Load the aggregate heat maps (each map is a data point to be clustered)
    agg_maps_fn = "agg_maps_homes.csv"
    agg_maps_path = os.path.join(metrics_dump, agg_maps_fn)
    csv.field_size_limit(sys.maxsize)
    with open(agg_maps_path) as fp:
         reader = csv.reader(fp, delimiter = ",", quotechar = '"')
         maps = [row for row in reader]
    # Grab 'dem headers
    headers = maps[0]
    # Grab 'dem maps
    maps = maps[1:len(maps)]
    # Create a column lookup dictionary (given data name, give column)
    column_idxs = {headers[i]: i for i in range(0, len(headers))}

    labels = []         # labels is list of labels (synchronized with all_samples) for each sample
    all_samples = []    # all_samples contains list of maps (data points)
    for m in maps:
        all_samples.append(ast.literal_eval(m[column_idxs["map"]]))
        labels.append(m[column_idxs["treatment"]] + "." + m[column_idxs["rep"]])
    # Turn labels and all_samples into numpy arrays (to do crazy pca math on)
    #  Not really necessary to do the same with labels (math is only done on all-samples), but I want to convince myself that labels and all_samples stay synchronized
    all_samples = np.asarray(all_samples)
    all_samples = np.transpose(all_samples) # This is the matrix we'll use for PCA
    labels = np.asarray(labels)
    labels = np.transpose(labels)
    full_num_dimensions = all_samples.shape[0]  # Grab the dimensionality of space we're working with

    # Calculate the means of each column (basically, the mean of each variable)
    means = []
    for i in range(0, all_samples.shape[0]):
        means.append([np.mean(all_samples[i,:])])
    mean_vector = np.asarray(means)
    # Calculate the eigen vectors (only do this if we have to... it takes a non-insignificant amount of time)
    if FORCE_GEN_EIGEN_VECTORS:
        scatter_matrix = np.zeros((full_num_dimensions, full_num_dimensions))
        for i in range(all_samples.shape[1]):
            scatter_matrix += (all_samples[:,i].reshape(full_num_dimensions, 1) - mean_vector).dot((all_samples[:,i].reshape(full_num_dimensions, 1) - mean_vector).T)
        print('Scatter Matrix:\n', scatter_matrix)
        # eigenvectors and eigenvalues for the from the scatter matrix
        eig_val_sc, eig_vec_sc = np.linalg.eig(scatter_matrix)
        for i in range(len(eig_val_sc)):
            eigvec_sc = eig_vec_sc[:,i].reshape(1, full_num_dimensions).T
            print('Eigenvector {}: \n{}'.format(i+1, eigvec_sc))
            print('Eigenvalue {} from scatter matrix: {}'.format(i+1, eig_val_sc[i]))
        np.save(agg_maps_fn.replace(".csv", "") + "__eig_val_sc.npy", eig_val_sc)
        np.save(agg_maps_fn.replace(".csv", "") + "__eig_vec_sc.npy", eig_vec_sc)
    else:
        try:
            eig_val_sc = np.load(agg_maps_fn.replace(".csv", "") + "__eig_val_sc.npy")
            eig_vec_sc = np.load(agg_maps_fn.replace(".csv", "") + "__eig_vec_sc.npy")
        except:
            scatter_matrix = np.zeros((full_num_dimensions, full_num_dimensions))
            for i in range(all_samples.shape[1]):
                scatter_matrix += (all_samples[:,i].reshape(full_num_dimensions, 1) - mean_vector).dot((all_samples[:,i].reshape(full_num_dimensions, 1) - mean_vector).T)
            print('Scatter Matrix:\n', scatter_matrix)
            # eigenvectors and eigenvalues for the from the scatter matrix
            eig_val_sc, eig_vec_sc = np.linalg.eig(scatter_matrix)
            for i in range(len(eig_val_sc)):
                eigvec_sc = eig_vec_sc[:,i].reshape(1, full_num_dimensions).T
                print('Eigenvector {}: \n{}'.format(i+1, eigvec_sc))
                print('Eigenvalue {} from scatter matrix: {}'.format(i+1, eig_val_sc[i]))
            np.save(agg_maps_fn.replace(".csv", "") + "__eig_val_sc.npy", eig_val_sc)
            np.save(agg_maps_fn.replace(".csv", "") + "__eig_vec_sc.npy", eig_vec_sc)

    # Make a list of (eigenvalue, eigenvector) tuples
    eig_pairs = [(np.abs(eig_val_sc[i]), eig_vec_sc[:,i]) for i in range(len(eig_val_sc))]
    # Get the sum of all of the eigen values (will help us calculated % variance explained)
    eig_vals_sum = sum([np.abs(eig_val_sc[i]) for i in range(len(eig_val_sc))])
    # Sort the (eigenvalue, eigenvector) tuples from high to low
    eig_pairs.sort(key = itemgetter(0), reverse = True)
    # print everything out
    for i in range(0, len(eig_pairs)):
        percent_var_explained = eig_pairs[i][0] / float(eig_vals_sum)
        if percent_var_explained < 0.001: break
        print "%d: %s (%s)" % (i, str(eig_pairs[i][0]), str(percent_var_explained))

    # How many dimensions from PCA are we going to use?
    dimensions_to_use = 37
    listy = []
    for i in range(0, dimensions_to_use):
        listy.append(np.asarray(eig_pairs[i][1]).reshape(full_num_dimensions, 1))
    tupy = tuple(listy)
    matrix_w = np.hstack(tupy)
    # Transform our data according to PCA stuff
    transformed = matrix_w.T.dot(all_samples)
    # Turn pca data into data for clustering
    cluster_data = []
    for ri in range(0, len(labels)):
        # for each label
        dp = transformed[:,ri]
        dp_vec = [float(dp[i]) for i in range(0, dp.shape[0])]
        label = labels[ri]
        cluster_data.append({"label": label, "data": dp_vec})

    # Cluster stuff
    kcluster = KMeansCluster(distanceMetric = distanceMetric, calculateCentroid = calcCentroid, data = cluster_data, force_k_bins = True)
    results = kcluster.run(num_bins = 5)
    # Report clustered things (treatment.rep)
    for cluster in results["cluster_results"]:
        print "CLUSTER: " + str(cluster["bin_id"])
        for thing in cluster["data"]:
            print "    %s" % (thing["label"])

    # plt.plot(transformed[0,0:60], transformed[1,0:60], 'o', markersize=7, color='blue', alpha=0.5, label='class1')
    # plt.xlabel('x_values')
    # plt.ylabel('y_values')
    # plt.legend()
    # plt.title('Transformed samples with class labels')
    # plt.show()

    # Plot clusters
    # results: {"cluster_results": [{"centroid": {"label": "", "data": []}, "data": [{"label": "", "data": []}]}, {}]}
    # treatment_shapes = {"T-256_G-1_A-64_P-0": "o", "T-256_G-1_A-64_P-1.0": "s","T-256_G-2_A-64_P-0": "D", "T-256_G-2_A-64_P-1.0": "*", "T-256_G-16_A-64_P-0": "^", "T-256_G-16_A-64_P-1.0": "+"}
    # cluster_colors = ["r", "b", "y", "g", "m", "c"]
    # plt.hold(True)
    # for ci in range(0, len(results["cluster_results"])):
    #     this_cluster = results["cluster_results"][ci]
    #     # Plot centroid
    #     centroid_x = this_cluster["centroid"]["data"][0]
    #     centroid_y = this_cluster["centroid"]["data"][1]
    #     plt.plot([centroid_x], [centroid_y], "x", color = cluster_colors[ci % len(cluster_colors)], alpha = 1.0)
    #     for point in this_cluster["data"]:
    #         pltlabel = point["label"].split(".rep")[0].replace("_U-50000", "")
    #         plt.plot([point["data"][0]], [point["data"][1]], marker = treatment_shapes[pltlabel], color = cluster_colors[ci % len(cluster_colors)], alpha = 0.5)
    #
    # plt.show()
