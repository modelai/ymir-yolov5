"""
convert object 365 dataset to yolov5 format

input directory:

object365
  - train
    - patch0
      - xxx.jpg
      - xxx.jpg
    - patch1
      - xxx.jpg
    - patchxxx
      - xxx.jpg
    - zhiyuan_objv2_train.json
  - val
    - patch0
      - xxx.jpg
      - xxx.jpg
    - patch1
      - xxx.jpg
    - patchxxx
      - xxx.jpg
    - zhiyun_objv2_val.json
  - object365_to_yolov5.py

output directory:

object365
  - train
    - images
      - xxx.jpg
    - labels
      - xxx.txt
  - val
    - images
      - xxx.jpg
    - labels
      - xxx.txt

run command:

python3 object365_to_yolov5.py
find train/images -name "*.jpg" > train.txt
find val/images -name "*.jpg" > val.txt
"""
from pathlib import Path

import numpy as np
import torch
from pycocotools.coco import COCO
from tqdm import tqdm


def clip_coords(boxes, shape):
    # Clip bounding xyxy bounding boxes to image shape (height, width)
    if isinstance(boxes, torch.Tensor):  # faster individually
        boxes[:, 0].clamp_(0, shape[1])  # x1
        boxes[:, 1].clamp_(0, shape[0])  # y1
        boxes[:, 2].clamp_(0, shape[1])  # x2
        boxes[:, 3].clamp_(0, shape[0])  # y2
    else:  # np.array (faster grouped)
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, shape[0])  # y1, y2


def xyxy2xywhn(x, w=640, h=640, clip=False, eps=0.0):
    # Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] normalized where xy1=top-left, xy2=bottom-right
    if clip:
        clip_coords(x, (h - eps, w - eps))  # warning: inplace clip
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[:, 0] = ((x[:, 0] + x[:, 2]) / 2) / w  # x center
    y[:, 1] = ((x[:, 1] + x[:, 3]) / 2) / h  # y center
    y[:, 2] = (x[:, 2] - x[:, 0]) / w  # width
    y[:, 3] = (x[:, 3] - x[:, 1]) / h  # height
    return y


# Make Directories
dir = Path('.')  # dataset root dir
for p in 'train', 'val':
    (dir / p).mkdir(parents=True, exist_ok=True)
    for q in 'images', 'labels':
        (dir / p / q).mkdir(parents=True, exist_ok=True)

# Train, Val Splits
for split, patches in [('train', 50 + 1), ('val', 43 + 1)]:
    print(f"Processing {split} in {patches} patches ...")
    images, labels = dir / split / 'images', dir / split / 'labels'
    download_dir = dir / split

    # Move
    for f in tqdm(download_dir.rglob('*.jpg'), desc=f'Moving {split} images'):
        f.rename(images / f.name)  # move to ./images/{split}

    # Labels
    coco = COCO(download_dir / f'zhiyuan_objv2_{split}.json')
    names = [x["name"] for x in coco.loadCats(sorted(coco.getCatIds()))]
    for cid, cat in enumerate(names):
        catIds = coco.getCatIds(catNms=[cat])
        imgIds = coco.getImgIds(catIds=catIds)
        for im in tqdm(coco.loadImgs(imgIds), desc=f'Class {cid + 1}/{len(names)} {cat}'):
            width, height = im["width"], im["height"]
            path = Path(im["file_name"])  # image filename
            try:
                with open(labels / path.with_suffix('.txt').name, 'a') as file:
                    annIds = coco.getAnnIds(imgIds=im["id"], catIds=catIds, iscrowd=None)
                    for a in coco.loadAnns(annIds):
                        x, y, w, h = a['bbox']  # bounding box in xywh (xy top-left corner)
                        xyxy = np.array([x, y, x + w, y + h])[None]  # pixels(1,4)
                        x, y, w, h = xyxy2xywhn(xyxy, w=width, h=height, clip=True)[0]  # normalized and clipped
                        file.write(f"{cid} {x:.5f} {y:.5f} {w:.5f} {h:.5f}\n")
            except Exception as e:
                print(e)
