import json, csv, os, errno
#import matplotlib.pyplot as plt
#from pandas import *

def ravi_script(dom_file = None):
    F=open(dom_file,"rt")
    theContent=F.read()
    F.close()
    temps=list()
    rows = theContent.split("\n")
    exp=rows[len(rows)-2].replace('[','')
    exp1=exp.replace('"','')
    exp2=exp1.replace(']','')
    exp3=exp2.split(',')

    i=8
    xLoc=[[],[],[]]
    yLoc=[[],[],[]]
    while(i<6152):
        if (i<1032):
            xLoc[0].append(int(exp3[i]))
        elif (i>=1032 and i<2056):
            xLoc[1].append(int(exp3[i]))
        elif (i>=2056 and i<3080):
            xLoc[2].append(int(exp3[i]))
        elif (i>=3080 and i<4104):
            yLoc[0].append(int(exp3[i]))
        elif (i>=4104 and i<5128):
            yLoc[1].append(int(exp3[i]))
        elif (i>=5128 and i<6152):
            yLoc[2].append(int(exp3[i]))
        i=i+1
    i=0
    j=0
    angCor=[[],[],[]]
    disCor=[[],[],[]]
    replicate=2

    while (i<1019):
        if ((((xLoc[replicate][i+5]-xLoc[replicate][i])**2 + (yLoc[replicate][i+5]-yLoc[replicate][i])**2)**0.5)!=0):
            angCor[replicate].append((xLoc[replicate][i+5]-xLoc[replicate][i])/(((xLoc[replicate][i+5]-xLoc[replicate][i])**2 + (yLoc[replicate][i+5]-yLoc[replicate][i])**2)**0.5))
        i=i+1

    i=0
    while (i<1019):
        disCor[replicate].append((((xLoc[replicate][i+5]-xLoc[replicate][i])**2 + (yLoc[replicate][i+5]-yLoc[replicate][i])**2)**0.5))
        i=i+1


    plt.plot(angCor[replicate])
    plt.axis([0,1100,-1.5,1.5])
    plt.xlabel("Movements")
    plt.ylabel("Angular Correlation")
    plt.show()

    plt.xlabel("Movements")
    plt.ylabel("Radial Distance")
    plt.plot(disCor[replicate])
    plt.show()
    #print(len(disCor[replicate]))
    #savefig('G4P0dis.png')

    #xf=np.fft.fft(angCor[replicate])
    #plot(xf)

def allison_script(dom_file = None):
    #########################################################
    # Heatmaps -- Allison
    #########################################################
    xDim = 80
    yDim = 80
    Lifespan = 1024
    trial = 0 #0-2
    dataList = []
    numTrials = 3 #always three replicates
    with open(dom_file, "r") as fp: #open final, becomes variable fp, will close file automatically
        data = csv.reader(fp ,delimiter=",", quotechar='"') #reads everything in file and writes it into 'data'
        for row in data:
            dataList.append(row) #this makes each row of data a segment of the list

    dataList=dataList[-1] #-1 means start from end of list instead of beginning, means dataList now only has last row- that's one we want

    allxLocs=dataList[8].strip("[]").split(",") #this strips away brackets and splits it by commas (the 8th term- xLocs)
    allyLocs=dataList[9].strip("[]").split(",")

    trialXLocs=[]
    trialYLocs=[]

    for t in range(0,numTrials): #this puts each replicates steps as a separate element in a list
        trialXLocs.append(allxLocs[t*Lifespan:(t+1)*Lifespan])
        trialYLocs.append(allyLocs[t*Lifespan:(t+1)*Lifespan])

    area = list()
    for x in range(xDim):
        area.append(list())
        for y in range(yDim):
            area[x].append(0)

    for j in range(Lifespan):
        xCor=int(trialXLocs[trial][j])
        yCor=int(trialYLocs[trial][j])
        area[xCor][yCor] = area[xCor][yCor] + 1
    #plt.imshow(area, interpolation="nearest")
    #plt.show()

    #########################################################
    # Revisit Histogram  -- Allison
    #########################################################
    numTimesRepeated=[]
    for i in range(1024):
        numTimesRepeated.append(0)

    for i in range(xDim):
        for j in range(yDim):
            numTimes=area[i][j]
            numTimesRepeated[numTimes] += 1
    # plt.bar([i for i in range(0, 1024)], numTimesRepeated)
    # plt.xlabel("Number of Times Visited")
    # plt.ylabel("Number of Squares")
    # plt.title("Distribution of Revisits")
    # plt.show()

def gen_revisit_metrics(dom = None, dump_loc = None, heatmaps = True, revisit_dist = True, env = None):
    '''
    This code was originally written by Allison. Modified by Alex.
    '''
    dimensions = (88, 88)
    # Break up trail paths (delimited by a -1)
    x_paths = dom["xLocation"].strip("[]").split(",")
    y_paths = dom["yLocation"].strip("[]").split(",")
    trail_paths = {"x_paths": [], "y_paths": []}
    for i in range(0, len(x_paths)):
        if x_paths[i] == "-1":
            trail_paths["x_paths"].append([])
            trail_paths["y_paths"].append([])
        else:
            trail_paths["x_paths"][-1].append(int(x_paths[i]))
            trail_paths["y_paths"][-1].append(int(y_paths[i]))
    # For each trail
    aggregate_area = [[0 for y in range(dimensions[1])] for x in range(dimensions[0])]
    aggregate_distribution = [0 for t in range(0, len(trail_paths["x_paths"][-1]) + 1)]
    for i in range(0, len(trail_paths["x_paths"])):
        area = [[0 for y in range(dimensions[1])] for x in range(dimensions[0])]
        distribution = [0 for t in range(0, len(trail_paths["x_paths"][i]) + 1)]
        # For each time point
        for k in range(0, len(trail_paths["x_paths"][i])):
            x = trail_paths["x_paths"][i][k]
            y = trail_paths["y_paths"][i][k]
            area[x][y] += 1
            aggregate_area[x][y] += 1
        # Save trail heatmap
        if heatmaps:
            # Save this image
            plt.imshow(area, interpolation = "nearest")
            plt.savefig(os.path.join(dump_loc, "%s__heatmap_%d.png" % (env, i)))
            plt.clf()
        # Save trial revisit distribution
        if revisit_dist:
            for ax in range(0, dimensions[0]):
                for ay in range(0, dimensions[1]):
                    distribution[area[ax][ay]] += 1
                    aggregate_distribution[area[ax][ay]] += 1
            plt.bar([n for n in range(0, 1025)], distribution)
            plt.xlabel("Number of Times Visited")
            plt.ylabel("Number of Squares")
            plt.title("Distribution of Revisits")
            plt.savefig(os.path.join(dump_loc, "%s__revisit_dist_%d.png" % (env, i)))
            plt.clf()
    if heatmaps:
        plt.imshow(aggregate_area, interpolation = "nearest")
        plt.savefig(os.path.join(dump_loc, "%s__heatmap_avg.png" % env))
        plt.clf()
    if revisit_dist:
        plt.bar([n for n in range(0, 1025)], aggregate_distribution)
        plt.xlabel("Number of Times Visited")
        plt.ylabel("Number of Squares")
        plt.title("Distribution of Revisits")
        plt.savefig(os.path.join(dump_loc, "%s__revisit_dist_sum.png" % env))
        plt.clf()

def gen_ang_autocorrelation_metrics(dom = None, dump_loc = None):
    '''
    Originally written by Ravi, modified by Alex
    '''
    # Break up trail paths (delimited by a -1)
    x_paths = dom["xLocation"].strip("[]").split(",")
    y_paths = dom["yLocation"].strip("[]").split(",")
    trial_paths = {"x_paths": [], "y_paths": []}
    for i in range(0, len(x_paths)):
        if x_paths[i] == "-1":
            trial_paths["x_paths"].append([])
            trial_paths["y_paths"].append([])
        else:
            trial_paths["x_paths"][-1].append(int(x_paths[i]))
            trial_paths["y_paths"][-1].append(int(y_paths[i]))

    window = 5
    for t in range(0, len(trial_paths["x_paths"])):
        angCor = []
        disCor = []
        xLoc = trial_paths["x_paths"][t]
        yLoc = trial_paths["y_paths"][t]
        for i in range(0, len(trial_paths["x_paths"][t]) - window):
            if ((((xLoc[i+5]-xLoc[i])**2 + (yLoc[i+5]-yLoc[i])**2)**0.5)!=0):
                angCor.append((xLoc[i+5]-xLoc[i])/(((xLoc[i+5]-xLoc[i])**2 + (yLoc[i+5]-yLoc[i])**2)**0.5))
                disCor.append((((xLoc[i+5]-xLoc[i])**2 + (yLoc[i+5]-yLoc[i])**2)**0.5))

        plt.axis([0,1100,-1.5,1.5])
        plt.xlabel("Movements")
        plt.ylabel("Angular Correlation")
        plt.plot(angCor)
        plt.savefig(os.path.join(dump_loc, "ang_correlation_%d.png" % t))
        plt.clf()

        plt.xlabel("Movements")
        plt.ylabel("Radial Distance")
        plt.plot(disCor)
        plt.savefig(os.path.join(dump_loc, "rad_dist_%d.png" % t))
        plt.clf()

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

if __name__ == "__main__":
    settings_fp = "param/settings.json"
    # Load up 'dem sett'ns
    with open(settings_fp) as fp:
        settings = json.load(fp)
    analysis_data_loc = settings["analysis"]["analysis_dump"]
    metrics_dump = settings["analysis"]["metrics_dump"]
    # ensure that analysis dump exists
    #dump_loc = settings["analysis"]["analysis_dump"]
    #mkdir_p(dump_loc)

    fitness_csv_content = "treatment,rep,env,fitness\n"
    revisit_csv_content = "treatment,rep,env,revisit_distribution\n"
    # Grab list of treatments in data location
    treatments = [tname for tname in os.listdir(analysis_data_loc) if os.path.isdir(os.path.join(analysis_data_loc, tname))]
    # Analyze treatment by treatment
    for treatment in treatments:
        print treatment
        treatment_loc = os.path.join(analysis_data_loc, treatment)
        replicates = [rname for rname in os.listdir(treatment_loc) if os.path.isdir(os.path.join(treatment_loc, rname))]
        # Analyze each replicate
        for rep in replicates:
            print rep
            rep_loc = os.path.join(treatment_loc, rep)

            # Analyze each environment organism was tested in
            envs = [ename for ename in os.listdir(rep_loc) if "env__" in ename]
            rep_metrics_dump = os.path.join(metrics_dump, treatment, rep)
            mkdir_p(rep_metrics_dump)
            for env in envs:
                print "ENV: " + str(env)
                env_loc = os.path.join(rep_loc, env)
                # Grab tested dom organism
                with open(os.path.join(env_loc, "dominant.csv"), "r") as fp:
                    reader = csv.reader(fp, delimiter = ",", quotechar = '"')
                    data = [row for row in reader]
                headers = data[0]
                dom = data[-1]
                # Dom dict contains final dominant organism for this treatment
                dom_dict = {headers[i]: dom[i] for i in range(0, len(headers))}
                ####################################
                # Run metrics
                ####################################
                #gen_revisit_metrics(dom = dom_dict, dump_loc = rep_metrics_dump, heatmaps = True, revisit_dist = True, env = env)
                #gen_ang_autocorrelation_metrics(dom = dom_dict, dump_loc = rep_metrics_dump, env = env)
                # Generate revist csv
                #  first parse location dicts
                x_path = dom_dict["xLocation"].strip("[]").split(",")
                y_path = dom_dict["yLocation"].strip("[]").split(",")
                #  both paths should be of equal length
                visit_dict = {}
                for t in range(0, len(x_path)):
                    if x_path[t] == "-1" or y_path[t] == "-1": continue
                    loc_id = x_path[t] + "," + y_path[t]
                    if not loc_id in visit_dict.keys(): visit_dict[loc_id] = 0
                    visit_dict[loc_id] += 1
                print "Sum of visits: " + str(sum(visit_dict.values()))
                revisit_dist = [0 for i in range(0, settings["analysis"]["org_lifespan"] + 1)]
                for visits in visit_dict.values(): 
                    try:
                        revisit_dist[visits] += 1
                    except:
                        print len(revisit_dist)
                        print visits
                        exit(-1)
                revisit_dist_str = str(revisit_dist).replace(" ", "")
                revisit_csv_content += "%s,%s,%s,\"%s\"\n" % (treatment, rep, env, revisit_dist_str)
                # Generate csv for this bro
                fitness = float(dom_dict["score"])
                fitness_csv_content += "%s,%s,%s,%f\n" % (treatment, rep, env, fitness)

    with open(os.path.join(metrics_dump, "fitness.csv"), "w") as fp:
        fp.write(fitness_csv_content)
    with open(os.path.join(metrics_dump, "revisit_distributions.csv"), "w") as fp:
        fp.write(revisit_csv_content)
    print ("DONE")
