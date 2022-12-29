#!/bin/bash

model=yolov5s
python3 -m torch.distributed.launch --master_port 12355 --nproc_per_node 2 train.py --weights ${model}.pt --cfg models/${model}.yaml --data data/Objects365-tiny.yaml --hyp data/hyps/hyp.scratch-low.yaml --epochs 3 --batch-size 64 --device 6,7 --sync-bn --workers 4 --name ${model}-tiny --exist-ok --noplots --cache ram
