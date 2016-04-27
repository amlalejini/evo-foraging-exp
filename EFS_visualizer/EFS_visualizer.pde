import java.util.*;

//ArrayList<HashMap<String, String>> orgs_to_draw = new ArrayList<HashMap<String, String>>();
ArrayList orgs_to_draw = new ArrayList();
int current_org = 0;
int zoom=8;
int mapSize=88;
color[] cols=new color[4];
Table table;
int t = 0;
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
        HashMap<String, String> org_map = new HashMap<String, String>();
        org_map.put("org_data_fp", org_data_fp);
        org_map.put("rep", rep);
        org_map.put("treatment", treatment);
        orgs_to_draw.add(org_map);
      }
    }
}

void draw(){
    String map = table.getString(t, "map");
    map = map.replace("[", "");
    map = map.replace("]", "");
    String[] tiles = map.split(",");
    noStroke();
    int z= 0;
    for (int i = 0; i < mapSize; i++) {
      for (int j = 0; j < mapSize; j++) {
        fill(cols[Integer.parseInt(tiles[z].trim())]);
        rect(j * zoom, i * zoom, zoom, zoom);
        z++;
      }
    }
    fill(cols[2]);
    rect(table.getInt(t, "yLocation") * zoom, table.getInt(t, "xLocation") * zoom, zoom, zoom);
    saveFrame("vid_dump/" + (String)((HashMap) orgs_to_draw.get(current_org)).get("treatment") + "/" + (String)((HashMap) orgs_to_draw.get(current_org)).get("rep") + "/" + "frame-" + t + ".png");
    t++;
    if (t >= table.getRowCount()) {
      current_org++;
      t = 0;
      if (current_org >= orgs_to_draw.size()) {
        exit();
      }
      table = loadTable((String)((HashMap) orgs_to_draw.get(current_org)).get("org_data_fp"), "header");
      println("SHOWING: " +  (String)((HashMap) orgs_to_draw.get(current_org)).get("org_data_fp"));
    }
}
