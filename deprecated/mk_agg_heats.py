import json, os, csv, ast

if __name__ == "__main__":
    settings_fp = "param/settings.json"
    # Load up the settings
    with open(settings_fp) as fp:
        settings = json.load(fp)
    metrics_dump = settings["analysis"]["metrics_dump"]
    world_width = settings["analysis"]["world_width"]
    test_envs_loc = settings["analysis"]["test_envs_loc"]

    paths_fpath = os.path.join(metrics_dump, "paths.csv")
    paths = None
    with open(paths_fpath) as fp:
         reader = csv.reader(fp, delimiter = ",", quotechar = '"')
         paths = [row for row in reader]
    headers = paths[0]
    paths = paths[1:len(paths)]
    # Create a column lookup dictionary (given data name, give column)
    column_idxs = {headers[i]: i for i in range(0, len(headers))}
    ####################################################################################################
    ####################################################################################################
    ####################################################################################################

    ####################################################################################################
    ####################################################################################################
    ####################################################################################################
    ###############################################
    # Make aggregated heat maps for each treatment (just home)
    agg_maps = {}
    for path in paths:
        # Extract relevant data:
        path_treatment = path[column_idxs["treatment"]]
        path_rep = path[column_idxs["rep"]]
        path_env = path[column_idxs["env"]]
        path_x = ast.literal_eval(path[column_idxs["x_path"]].replace("-1,", ""))
        path_y = ast.literal_eval(path[column_idxs["y_path"]].replace("-1,", ""))
        if path_env.replace("env__", "") != path_treatment.replace("_U-50000", ""): continue
        #if len(set(path_x)) == 1 and len(set(path_y)) == 1: continue
        # Have we processed this treatment before?
        if not path_treatment in agg_maps:
            # Add treatment to dictionary
            agg_maps[path_treatment] = {}
        # Have we processed this replicate before?
        if not path_rep in agg_maps[path_treatment]:
            # Make a new aggregate map for this replicate
            agg_maps[path_treatment][path_rep] = [[0 for _ in range(0, world_width)] for _ in range(0, world_width)]
        # add path to map
        for i in range(0, len(path_x)):
            agg_maps[path_treatment][path_rep][path_y[i]][path_x[i]] += 1
    # # Sanity check for above functionality
    # for t in agg_maps:
    #     for k in agg_maps[t]:
    #         print "%s.%s: %d" % (t, k, sum(map(sum, agg_maps[t][k])))
    ###############################################
    # Normalize the HEAT for aggregated maps
    # for t in agg_maps:
    #     for r in agg_maps[t]:
    #         vtot = sum(map(sum, agg_maps[t][r]))
    #         agg_maps[t][r] = [ [agg_maps[t][r][y][x] / float(vtot) for x in range(0, len(agg_maps[t][r][y]))] for y in range(0, len(agg_maps[t][r]))]
    # # Sanity check for above functionality
    # for t in agg_maps:
    #     for k in agg_maps[t]:
    #         print "%s.%s: %f" % (t, k, sum(map(sum, agg_maps[t][k])))
    ###############################################
    # # Flatten aggretaged heatmaps
    # flat_agg_maps = {}
    # for t in agg_maps:
    #     flat_agg_maps[t] = {}
    #     for r in agg_maps[t]:
    #         flat_agg_maps[t][r] = [(x / 87.0, y / 87.0, agg_maps[t][r][y][x]) for y in range(0, len(agg_maps[t][r])) for x in range(0, len(agg_maps[t][r][y]))]
    # ###############################################
    # # Write out aggregated heatmaps to file
    # csv_content = "treatment,rep,map\n"
    # for t in flat_agg_maps:
    #     for r in flat_agg_maps[t]:
    #         csv_content += "%s,%s,\"%s\"\n" % (t, r, str(flat_agg_maps[t][r]).replace(" ", ""))
    # with open(os.path.join(metrics_dump, "agg_maps.csv"), "w") as fp:
    #     fp.write(csv_content)
    ###############################################
    # Flatten aggretaged heatmaps and toss the x y values
    flat_agg_maps = {}
    for t in agg_maps:
        flat_agg_maps[t] = {}
        for r in agg_maps[t]:
            flat_agg_maps[t][r] = [agg_maps[t][r][y][x] for y in range(0, len(agg_maps[t][r])) for x in range(0, len(agg_maps[t][r][y]))]
    ###############################################
    # Write out aggregated heatmaps to file
    csv_content = "treatment,rep,map\n"
    for t in flat_agg_maps:
        for r in flat_agg_maps[t]:
            csv_content += "%s,%s,\"%s\"\n" % (t, r, str(flat_agg_maps[t][r]).replace(" ", ""))
    with open(os.path.join(metrics_dump, "agg_maps_homes.csv"), "w") as fp:
        fp.write(csv_content)
    # try with no g-16-p0
    csv_content = "treatment,rep,map\n"
    for t in flat_agg_maps:
        if t == "T-256_G-16_A-64_P-0_U-50000":
            print "Leave out this one!"
            continue
        for r in flat_agg_maps[t]:
            csv_content += "%s,%s,\"%s\"\n" % (t, r, str(flat_agg_maps[t][r]).replace(" ", ""))
    with open(os.path.join(metrics_dump, "agg_maps_homes-NOG16P0.csv"), "w") as fp:
        fp.write(csv_content)
    ####################################################################################################
    ####################################################################################################
    ####################################################################################################

    ###############################################
    # Make heat map for each environment
    test_envs_maps = {}
    for path in paths:
        # Extract relevant data:
        path_treatment = path[column_idxs["treatment"]]
        path_rep = path[column_idxs["rep"]]
        path_env = path[column_idxs["env"]]
        path_x = ast.literal_eval(path[column_idxs["x_path"]].replace("-1,", ""))
        path_y = ast.literal_eval(path[column_idxs["y_path"]].replace("-1,", ""))
        # have we seen something like this before?
        if not path_env in test_envs_maps:
            test_envs_maps[path_env] = {}
        if not path_treatment in test_envs_maps[path_env]:
            test_envs_maps[path_env][path_treatment] = {}
        if not path_rep in test_envs_maps[path_env][path_treatment]:
            test_envs_maps[path_env][path_treatment][path_rep] = [[0 for _ in range(0, world_width)] for _ in range(0, world_width)]
        # Add path to map
        for i in range(0, len(path_x)):
            test_envs_maps[path_env][path_treatment][path_rep][path_y[i]][path_x[i]] += 1
        this_map = test_envs_maps[path_env][path_treatment][path_rep]
        # Flatten
        flat = [this_map[y][x] for y in range(0, len(this_map)) for x in range(0, len(this_map[y]))]
        test_envs_maps[path_env][path_treatment][path_rep] = flat

    ###############################################
    # Write out aggregated heatmaps to file
    for env in test_envs_maps:
        csv_content = "treatment,rep,env,map\n"
        for t in test_envs_maps[env]:
            for r in test_envs_maps[env][t]:
                csv_content += "%s,%s,%s,\"%s\"\n" % (t, r, env, str(test_envs_maps[env][t][r]).replace(" ", ""))
        with open(os.path.join(metrics_dump, "agg_maps_%s.csv" % env), "w") as fp:
            fp.write(csv_content)
    print "DONE"
