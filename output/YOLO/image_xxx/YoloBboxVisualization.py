import os
import argparse
import cv2
import numpy as np


def get_file_list(seq_name, file_extension):
    whole_file_list = []
    files = os.listdir(seq_name)
    for file in files:
        path = os.path.join(seq_name, file)
        whole_file_list.append(path)
    data_file_list = [file for file in whole_file_list if file.endswith(file_extension)]
    data_file_list.sort()
    return data_file_list


def get_bounding_box_drawn_frame_xyxy(frame, top_left, bottom_right, box_color, line_thick):
    temp = np.copy(frame)
    cv2.rectangle(temp, top_left, bottom_right, box_color, line_thick)
    return temp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sequence_name", help="Input sequence name. (i.e. C1_1-1)")
    args = parser.parse_args()

    current_path = os.getcwd()
    output_path = current_path+"/output_"+args.sequence_name
    os.makedirs(output_path, exist_ok=True)  # create output folder

    img_file_list = get_file_list(args.sequence_name, ".jpg")
    ann_file_list = get_file_list(args.sequence_name, ".txt")

    for i in range(len(img_file_list)):
        img = cv2.imread(img_file_list[i])
        ann_file = open(ann_file_list[i], "r")
        cx, cy, bw, bh = np.array(ann_file.readlines()[0].split(" "), dtype=float)[1:]
        ann_file.close()

        h, w, _ = img.shape
        cx *= w
        bw *= w
        cy *= h
        bh *= h

        top_left = (int(cx-bw/2), int(cy-bh/2))
        bottom_right = (int(cx+bw/2), int(cy+bh/2))

        result = get_bounding_box_drawn_frame_xyxy(img, top_left, bottom_right, (0, 255, 255), 4)
        cv2.imwrite(output_path+"/"+img_file_list[i].split("/")[-1], result)
