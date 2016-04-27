from cluster import *
import math, csv, ast, json, os

'''
Example usage/testing of cluster.py
'''

def aggHMDist(a, b):
    return math.sqrt(sum([(a["map"][i][2] - b["map"][i][2])**2 for i in range(0, len(a["map"]))]))

def aggHMCentroid(l):
    cen = []
    for i in range(0, len(l[0]["map"])):
        tot = 0
        for mem in l:
            tot += mem["map"][i][2]
        cen.append( (l[0]["map"][i][0], l[0]["map"][i][1], tot / float(len(l))) )
    return {"map": cen, "treatment": "centroid", "rep": "centroid"}

if __name__ == "__main__":
    # Load data
    settings_fp = "param/settings.json"
    with open(settings_fp) as fp:
        settings = json.load(fp)

    with open(os.path.join(settings["analysis"]["metrics_dump"], "agg_maps_homes.csv"), "r") as fp:
        reader = csv.reader(fp, delimiter = ",", quotechar = '"')
        data = [row for row in reader]

    header = data[0]
    data = data[1:len(data)]
    # Make column look-up table
    col_lu = {header[i]: i for i in range(0, len(header))}
    # Put data into expected format
    cdata = [{"treatment": dp[col_lu["treatment"]], "rep": dp[col_lu["rep"]], "map": ast.literal_eval(dp[col_lu["map"]])} for dp in data]
    print len(cdata)
    # Cluster data
    kcluster = KMeansCluster(distanceMetric = aggHMDist, calculateCentroid = aggHMCentroid, data = cdata, force_k_bins = False)
    results = kcluster.run(num_bins = 6)

    # Report clustered things (treatment.rep)
    for cluster in results["cluster_results"]:
        print "CLUSTER: " + str(cluster["bin_id"])
        for thing in cluster["data"]:
            print "    %s.%s" % (thing["treatment"], thing["rep"])
