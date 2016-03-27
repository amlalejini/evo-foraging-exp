import json, os, errno, subprocess

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
    frames_loc = settings["analysis"]["vid_frame_dump"]
    mkdir_p(settings["analysis"]["vid_dump"])
    treatments = [tname for tname in os.listdir(frames_loc) if os.path.isdir(os.path.join(frames_loc, tname))]
    for treatment in treatments:
        print treatment
        treatment_loc = os.path.join(frames_loc, treatment)
        replicates = [rname for rname in os.listdir(treatment_loc) if os.path.isdir(os.path.join(treatment_loc, rname))]
        for rep in replicates:
            print rep
            rep_loc = os.path.join(treatment_loc, rep)
            # rename files (to be consistent with what ffmpeg is expecting)
            vid_name = os.path.join(settings["analysis"]["vid_dump"], "%s__%s__vid.mp4" % (treatment, rep))
            cmd = "ffmpeg -i %s -r 34 -threads 4 %s" % (os.path.join(rep_loc, "frame-%d.png"), vid_name)
            process = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
            output, err = process.communicate()
    print ("DONE")
