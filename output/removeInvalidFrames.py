import os
import argparse
import numpy as np
from collections import Counter


def get_file_list(folder_path, file_extension):
    whole_file_list = []
    files = os.listdir(folder_path)
    for file in files:
        path = os.path.join(folder_path, file)
        whole_file_list.append(path)
    data_file_list = [file for file in whole_file_list if file.endswith(file_extension)]
    data_file_list.sort()
    return data_file_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sequence_name", help="Input sequence name. (i.e. C1_1-1)")
    parser.add_argument("-ifn", "--invalid_frame_num", help="Input invalid frame numbers. (i.e. 1,2,4,10,22,...)")
    args = parser.parse_args()

    current_path = os.getcwd()
    trackeval_gt_file_path = current_path+"/TrackEval/"+args.sequence_name+"/gt/gt.txt"
    yolo_path = current_path+"/YOLO/image_xxx/"+args.sequence_name

    trackeval_gt_file = open(trackeval_gt_file_path, "r")
    gt_txt_list = trackeval_gt_file.readlines()
    trackeval_gt_file.close()
    gt_txt_list_each_element = np.array(list(map(lambda gt_line: gt_line.replace("\n", "").split(" "), gt_txt_list)))

    invalid_frame_list = args.invalid_frame_num.split(",")
    invalid_frame_index_in_gt_txt_list = sorted(np.where(np.isin(gt_txt_list_each_element[:, 0], invalid_frame_list) == True)[0].tolist(), reverse=True)

    for i in invalid_frame_index_in_gt_txt_list:
        del gt_txt_list[i]

    current_tracking_id = 1
    gt_txt_list_each_element = np.array(list(map(lambda gt_line: gt_line.replace("\n", "").split(" "), gt_txt_list)))
    first_invalid_tracking_id_index_in_gt_txt_list_each_element = None
    for i, gt_txt in enumerate(gt_txt_list_each_element):
        if int(gt_txt[1])-current_tracking_id >= 2:
            current_tracking_id += 1
            first_invalid_tracking_id_index_in_gt_txt_list_each_element = i
            break
        else:
            current_tracking_id = int(gt_txt[1])

    invalid_tracking_id_list = list(map(int, gt_txt_list_each_element[first_invalid_tracking_id_index_in_gt_txt_list_each_element:, 1]))
    invalid_tracking_id_list_count = sorted(Counter(invalid_tracking_id_list).items())
    modified_tracking_id_list = []
    for invalid_tracking_id, invalid_tracking_id_num in invalid_tracking_id_list_count:
        for _ in range(invalid_tracking_id_num):
            modified_tracking_id_list.append(str(current_tracking_id))
        current_tracking_id += 1

    gt_txt_list_each_element[first_invalid_tracking_id_index_in_gt_txt_list_each_element:, 1] = np.array(modified_tracking_id_list)
    gt_txt_list_each_element = gt_txt_list_each_element.tolist()

    gt_modified_txt = "\n".join(" ".join(element for element in gt_line) for gt_line in gt_txt_list_each_element)
    trackeval_gt_file = open(trackeval_gt_file_path, "w")
    trackeval_gt_file.write(gt_modified_txt)
    trackeval_gt_file.close()

    yolo_img_file_path_list = get_file_list(yolo_path, ".jpg")
    yolo_gt_file_path_list = get_file_list(yolo_path, ".txt")

    for i in range(len(yolo_img_file_path_list)):
        if str(int(yolo_img_file_path_list[i].split("/")[-1][:-4])) in invalid_frame_list:
            os.remove(yolo_img_file_path_list[i])
        if str(int(yolo_gt_file_path_list[i].split("/")[-1][:-4])) in invalid_frame_list:
            os.remove(yolo_gt_file_path_list[i])
