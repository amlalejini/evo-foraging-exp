String filename="G16_P1_R10_org-0_trial-0_analysis.csv";
ArrayList<String> orgs_to_draw = new ArrayList<String>();
Table table;
int t=0;
int zoom=8;
int mapSize=88;
color[] cols=new color[4];
//time,foodCollected,xLocation,yLocation,mapSize,map
void setup(){
    String exp_path = "/home/parallels/Desktop/probgates/";
    File exp_dir = new File(exp_path);
    String[] treatments = exp_dir.list();    
    for (String treatment : treatments) {
      String treatment_path = exp_path + treatment + "/";
      File treatment_dir = new File(treatment_path);
      String[] reps = treatment_dir.list();
      for (String rep : reps) {
        String rep_analysis_path = treatment_path + rep + "/analysis/";
        String org_data_fp = rep_analysis_path + "org-0_trial-0_analysis.csv";
        orgs_to_draw.add(org_data_fp);      
      }
    }
    println(orgs_to_draw);
    size(704,704);
    table = loadTable(filename, "header");
    cols[0]=color(0,0,0);
    cols[1]=color(10,200,50); //gras
    cols[2]=color(200,100,100); //dude
    cols[3]=color(128,128,128);
    exit();
    
}

void draw(){
    String map=table.getString(t,"map");
    map=map.replace('[',' ');
    map=map.replace(']',' ');
    String[] tiles=map.split(",");
    noStroke();
    int z=0;
    for(int i=0;i<mapSize;i++){
        for(int j=0;j<mapSize;j++){
            fill(cols[Integer.parseInt(tiles[z].trim())]);
            rect(j*zoom,i*zoom,zoom,zoom);
            z++;
        }
    }
    fill(cols[2]);
    rect(table.getInt(t,"yLocation")*zoom,table.getInt(t,"xLocation")*zoom,zoom,zoom);
    t++;
    //uncommen the line below to save all the frames
    saveFrame("frame-####.png");
    if(t>=table.getRowCount()){
        exit();
    }
}