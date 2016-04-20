import json, os, csv, ast, sys, math
import numpy as np
import matplotlib.pyplot as plt
from operator import itemgetter
from cluster import *

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
    # Load up the settings
    with open(settings_fp) as fp:
        settings = json.load(fp)
    metrics_dump = settings["analysis"]["metrics_dump"]
    world_width = settings["analysis"]["world_width"]

    agg_maps_path = os.path.join(metrics_dump, "agg_maps2.csv")
    csv.field_size_limit(sys.maxsize)
    with open(agg_maps_path) as fp:
         reader = csv.reader(fp, delimiter = ",", quotechar = '"')
         maps = [row for row in reader]
    headers = maps[0]
    maps = maps[1:len(maps)]
    # Create a column lookup dictionary (given data name, give column)
    column_idxs = {headers[i]: i for i in range(0, len(headers))}

    labels = []
    all_samples = []
    for m in maps:
        all_samples.append(ast.literal_eval(m[column_idxs["map"]]))
        labels.append(m[column_idxs["treatment"]] + "." + m[column_idxs["rep"]])

    all_samples = np.asarray(all_samples)
    all_samples = np.transpose(all_samples)
    labels = np.asarray(labels)
    labels = np.transpose(labels)

    # Now we have correct matrix for pca
    means = []
    for i in range(0, all_samples.shape[0]):
        means.append([np.mean(all_samples[i,:])])
    mean_vector = np.asarray(means)

    # scatter_matrix = np.zeros((7744, 7744))
    # for i in range(all_samples.shape[1]):
    #     scatter_matrix += (all_samples[:,i].reshape(7744,1) - mean_vector).dot((all_samples[:,i].reshape(7744,1) - mean_vector).T)
    # print('Scatter Matrix:\n', scatter_matrix)
    # # eigenvectors and eigenvalues for the from the scatter matrix
    # eig_val_sc, eig_vec_sc = np.linalg.eig(scatter_matrix)
    # for i in range(len(eig_val_sc)):
    #     eigvec_sc = eig_vec_sc[:,i].reshape(1,7744).T
    #     print('Eigenvector {}: \n{}'.format(i+1, eigvec_sc))
    #     print('Eigenvalue {} from scatter matrix: {}'.format(i+1, eig_val_sc[i]))
    # np.save("eig_val_sc.npy", eig_val_sc)
    # np.save("eig_vec_sc.npy", eig_vec_sc)

    eig_val_sc = np.load("eig_val_sc.npy")
    eig_vec_sc = np.load("eig_vec_sc.npy")

    # Make a list of (eigenvalue, eigenvector) tuples
    eig_pairs = [(np.abs(eig_val_sc[i]), eig_vec_sc[:,i]) for i in range(len(eig_val_sc))]
    # Sort the (eigenvalue, eigenvector) tuples from high to low
    eig_pairs.sort(key = itemgetter(0), reverse = True)
    # for i in range(0, len(eig_pairs)):
    #     print "%d: %s" % (i, str(eig_pairs[i][0]))
        #if eig_pairs[i][0] < 10: break
    #matrix_w = np.hstack(eig_pairs[0:46][1])
    listy = []
    for i in range(0, 30):
        listy.append(np.asarray(eig_pairs[i][1]).reshape(7744,1))
    tupy = tuple(listy)
    matrix_w = np.hstack(tupy)
    #print tuple(eig_pairs[0:46][1])
    #matrix_w = np.hstack(( eig_pairs[0][1].reshape(7744,1), eig_pairs[1][1].reshape(7744,1), eig_pairs[2][1].reshape(7744,1), eig_pairs[3][1].reshape(7744,1), eig_pairs[4][1].reshape(7744,1), eig_pairs[5][1].reshape(7744,1), eig_pairs[6][1].reshape(7744,1) ))
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
    results = kcluster.run(num_bins = 8)
    # Report clustered things (treatment.rep)
    for cluster in results["cluster_results"]:
        print "CLUSTER: " + str(cluster["bin_id"])
        for thing in cluster["data"]:
            print "    %s" % (thing["label"])

    plt.plot(transformed[0,0:60], transformed[1,0:60], 'o', markersize=7, color='blue', alpha=0.5, label='class1')
    plt.xlabel('x_values')
    plt.ylabel('y_values')
    plt.legend()
    plt.title('Transformed samples with class labels')
    plt.show()
