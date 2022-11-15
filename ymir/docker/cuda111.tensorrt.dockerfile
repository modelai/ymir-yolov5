ARG baseimage=20.12-py3
# yolov5 recommended for 21.08-py3, here we use py3.8 + cuda11.1.1 + pytorch1.8.0
# view https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel_20-12.html#rel_20-12 for details
FROM nvcr.io/nvidia/pytorch:${baseimage}
ARG YMIR="1.1.0"
ENV PYTHONPATH=.
ENV YMIR_VERSION=$YMIR
# fix font download directory
ENV YOLOV5_CONFIG_DIR='/app/data'

# change apt and pypy mirrors
RUN sed -i 's#http://archive.ubuntu.com#https://mirrors.ustc.edu.cn#g' /etc/apt/sources.list \
    && sed -i 's#http://security.ubuntu.com#https://mirrors.ustc.edu.cn#g' /etc/apt/sources.list \
    && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# apt install required packages
RUN apt update && \
    apt install -y zip htop vim libgl1-mesa-glx

# install ymir-exc
RUN pip install "git+https://github.com/modelai/ymir-executor-sdk.git@ymir1.3.0"

COPY . /yolov5
# pip install required packages
RUN pip install -r /yolov5/requirements.txt && \
    mkdir -p /img-man && \
    mv /yolov5/ymir/img-man/*.yaml /img-man && \
    mkdir -p ${YOLOV5_CONFIG_DIR} && \
    mv /yolov5/ymir/*.ttf ${YOLOV5_CONFIG_DIR} && \
    mv /yolov5/ymir/*.pt /yolov5 && \
    echo "cd /yolov5 && python3 ymir/start.py" > /usr/bin/start.sh

WORKDIR /yolov5

# overwrite entrypoint to avoid ymir1.1.0 import docker image error.
ENTRYPOINT []
CMD bash /usr/bin/start.sh
