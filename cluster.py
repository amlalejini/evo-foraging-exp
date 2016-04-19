import random, copy

'''
TODO:
'''

class KMeansCluster(object):

    def __init__(self, distanceMetric, calculateCentroid, data, force_k_bins = False):
        '''
        Param: distanceMetric is the function that will be used to calculate data distances
         * Distance metric must return an int/float
        Param: calculateCentroid is a function that will be used to calculated a centroid point from a list of data points
         * calculateCentroid must return a data point that is in the same format as all data points provided in data
        Param: force_k
         * If we force k, we never let # of bins fall below k
           * when we would get an empty bin, put the bigget outlier in it from one of the other bins (that would not make the other bin empty)
         * If we don't force k, empty bins will be purged
        '''
        self.distanceMetric = distanceMetric
        self.calculateCentroid = calculateCentroid
        self.data = data
        self.force_k = force_k_bins

    def run(self, num_bins = 3):
        '''
        K-means clustering algorithm:
         * Initialize bins
         * Repeat:
           * Refine bin assignments
           * Update bin centroids
           * If no data points moved, stop
        '''
        # Check that num_bins >= len(data)
        if num_bins > len(self.data) or num_bins == 0:
            print "Number of bins must be <= length of data and cannot be 0!"
            return -1
        # Initialize k bins
        bins = [{"data": [], "centroid": None, "bin_id": i} for i in range(0, num_bins)]
        # Randomly assign data to bins -- spin the wheel!
        for datum in self.data: random.choice(bins)["data"].append(datum)
        # Make sure nothing is empty
        for bi in range(0, len(bins)):
            if len(bins[bi]["data"]) == 0:
                # find largest bin, divide in half, move half of values here
                max_len_i = 0
                for mi in range(0, len(bins)):
                    if len(bins[mi]["data"]) > len(bins[max_len_i]["data"]): max_len_i = mi
                # divide in half and move half of data
                bins[bi]["data"] = bins[max_len_i]["data"][:len(bins[max_len_i]["data"]) / 2]
                del bins[max_len_i]["data"][:len(bins[max_len_i]["data"]) / 2]
        # Initialize centroids
        for b in bins: b["centroid"] = self.calculateCentroid(b["data"])
        # Cluster loop
        iters = 0
        while True:
            iters += 1
            print "ITER: " + str(iters)
            # 1) Refine assignments
            new_bins = [{"data": [], "centroid": bins[i]["centroid"], "bin_id": bins[i]["bin_id"]} for i in range(0, len(bins))]
            something_moved = False
            for bi in range(0, len(bins)):
                for datum in bins[bi]["data"]:
                    # Where does this data point belong?
                    best_fit = bi
                    best_fit_dist = self.distanceMetric(bins[best_fit]["centroid"], datum)
                    for ni in range(0, len(new_bins)):
                        this_bin_centroid = bins[ni]["centroid"]
                        this_bin_dist = self.distanceMetric(this_bin_centroid, datum)
                        if this_bin_dist < best_fit_dist:
                            best_fit = ni
                            best_fit_dist = this_bin_dist
                            something_moved = True
                    # Assign data point to where it best fits
                    new_bins[best_fit]["data"].append(copy.deepcopy(datum))
            bins = new_bins
            #print "Bins post-refinement: " + str(bins)
            # 2) Update centroids and resolve empty bins
            if self.force_k:
                # We're forcing there to be k bins; handle bins accordingly
                # Collect the empty bins; calculate centroid for non-empty bins we see along the way
                empty_bins = []
                nonempty_bins = []
                for bi in range(0, len(bins)):
                    if len(bins[bi]["data"]) == 0:
                        empty_bins.append(bi)
                    else:
                        bins[bi]["centroid"] = self.calculateCentroid(bins[bi]["data"])
                        nonempty_bins.append(bi)
                # Resolve the empty bins
                for e_i in empty_bins:
                    something_moved = True
                    #print "There was an empty bin!"
                    # Recruit a new member!
                    biggest_dev = {"cluster_i": -1, "data_i": -1, "deviation": -1}
                    for n_i in nonempty_bins:
                        # Find largest deviation (skip bins of length 1)
                        if not len(bins[n_i]["data"]) > 1: continue
                        big_dev = self._find_largest_bin_outlier(bins[n_i])
                        if big_dev["deviation"] > biggest_dev["deviation"]:
                            biggest_dev = {"cluster_i": n_i, "data_i": big_dev["i"], "deviation": big_dev["deviation"]}
                    # Move new recruit from prev cluster to new cluster
                    bins[e_i]["data"].append(bins[biggest_dev["cluster_i"]]["data"][biggest_dev["data_i"]])
                    del bins[biggest_dev["cluster_i"]]["data"][biggest_dev["data_i"]]
                    # Update bin centroids (previously empty bin, and bin we took the data point from)
                    bins[e_i]["centroid"] = self.calculateCentroid(bins[e_i]["data"])
                    bins[biggest_dev["cluster_i"]]["centroid"] = self.calculateCentroid(bins[biggest_dev["cluster_i"]]["data"])
            else:
                # We do not force K: update non-empty bins, delete empty bins
                for bi in range(len(bins) - 1, -1, -1):
                    if len(bins[bi]["data"]) == 0:
                        del bins[bi]
                    else:
                        # Bin is not empty, update its centroid
                        bins[bi]["centroid"] = self.calculateCentroid(bins[bi]["data"])
            #print "Bins post centroid update: " + str(bins)
            # Are we done?
            if not something_moved: break
        # return all 'dem clusters
        return {"cluster_results": bins, "convergence_time": iters}

    def _find_largest_bin_outlier(self, b):
        big_dev = -1
        big_dev_val = -1
        for d in range(0, len(b["data"])):
            this_dev = self.distanceMetric(b["data"][d], b["centroid"])
            if this_dev > big_dev_val:
                big_dev = d
                big_dev_val = this_dev
        return {"i": big_dev, "deviation": big_dev_val}
