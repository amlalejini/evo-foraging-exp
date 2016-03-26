import json, csv, os
import matplotlib.pyplot as plt
from pandas import *

def parse_fitness_csv(dom_file, treatment_name, rep, env):
    with open(dom_file, "r") as fp:
        reader = csv.reader(fp ,delimiter=",", quotechar='"') #reads everything in file and writes it into 'data'
        data = [row for row in reader]
    data = data[-1]
    return float(data[5])

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

if __name__ == "__main__":
    settings_fp = "param/settings.json"
    # Load up 'dem sett'ns
    with open(settings_fp) as fp:
        settings = json.load(fp)
    data_loc = settings["analysis"]["exp_data_location"]

    csv_content = "treatment,rep,env,fitness\n"

    # Grab list of treatments in data location
    treatments = [tname for tname in os.listdir(data_loc) if os.path.isdir(os.path.join(data_loc, tname))]
    # Analyze treatment by treatment
    for treatment in treatments:
        print treatment
        treatment_loc = os.path.join(data_loc, treatment)
        replicates = [rname for rname in os.listdir(treatment_loc) if os.path.isdir(os.path.join(treatment_loc, rname))]
        # Analyze each replicate
        for rep in replicates:
            print rep
            rep_loc = os.path.join(treatment_loc, rep)

            dom_file = os.path.join(rep_loc, "output", "dominant.csv")
            #allison_script(dom_file)
            #ravi_script(dom_file)
            env = "_".join(treatment.split("_")[0:-1])
            fitness = parse_fitness_csv(dom_file, treatment, rep, treatment)
            csv_content += "%s,%s,%s,%f\n" % (treatment, rep, env, fitness)

    with open("fitnesses.csv", "w") as fp:
        fp.write(csv_content)
