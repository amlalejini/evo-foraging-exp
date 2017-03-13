from PIL import Image
import numpy as np
import os, PIL, csv, errno, subprocess

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def main():
    # Settings
    exp_dir = "/Users/amlalejini/DataPlayground/evo-foraging-strats"
    analysis_dir = os.path.join(exp_dir, "efs_analysis")
    vids_dir = os.path.join(exp_dir, "vids")
    map_w = 81
    color_map = {1: (27,158,119), 0: (0, 0, 0), "agent": (166,206,227)}
    mkdir_p(vids_dir)
    # Runs:
    runs = [r for r in os.listdir(analysis_dir) if "_rep_" in r]
    for run in runs:
        print "Processing run: %s" % run
        run_dir = os.path.join(analysis_dir, run)
        envs = [e for e in os.listdir(run_dir) if "env__" in e]
        for env in envs:
            env_dir = os.path.join(run_dir, env)
            # Get the trial analysis file.
            files = [f for f in os.listdir(env_dir) if "org" in f and "analysis.csv" in f]
            fname = files[0]
            print fname
            data = None
            with open(os.path.join(env_dir, fname), "r") as fp:
                reader = csv.reader(fp, delimiter = ",", quotechar = '"')
                data = [row for row in reader]
            header = data[0]
            data = data[1:]
            col_lu = {header[i]: i for i in range(0, len(header))}

            # Make location for frames.
            frames_dir = os.path.join(vids_dir, run, env, "frames")
            mkdir_p(frames_dir)
            for t in range(0, len(data)):
                m = data[t][col_lu["map"]].strip("[]").split(",")
                x = int(data[t][col_lu["xLocation"]])
                y = int(data[t][col_lu["yLocation"]])
                height = map_w
                width = map_w
                im = Image.new(mode = "RGB", size = (width, height))
                #m1 = [[color_map[int(m[row * width + d])] for d in range(0, width)] for row in range(0, height)]
                for row in range(0, height):
                    for col in range(0, width):
                        im.putpixel((col, row), color_map[int(m[row * width + col])])
                if (x >= 0 and x <= width) and (y >= 0 and y <= height): im.putpixel((x, y), color_map["agent"])
                im = im.resize((600, 600), resample = PIL.Image.NEAREST)
                im.save(os.path.join(frames_dir, "frame-%d.png" % t), "PNG")
            vid_name = "%s____%s.mp4" % (run, env)
            cmd = "./ffmpeg -i %s -r 34 -threads 4 %s" % (os.path.join(frames_dir, "frame-%d.png"), vid_name)
            return_code = subprocess.call(cmd, shell = True)
            # Clean up temp analysis file.
            return_code = subprocess.call("rm *.png", shell = True, cwd = frames_dir)
            exit()

    #exit
    # size = None
    # im = Image.new(mode = "RGB", size = (50, 50))
    # #im.show()
    # im.putpixel((25, 25), (100, 100, 0))
    # im.show()
    # im2 = im.resize((200, 200), resample = PIL.Image.BICUBIC)
    # im2.show()

if __name__ == "__main__":
    main()
