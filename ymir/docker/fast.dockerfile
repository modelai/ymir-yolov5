# docker build -t youdaoyzbx/ymir-executor:ymir2.1.0-yolov5-v7.0-cu111-tmi -f ymir/docker/fast.dockerfile .
FROM youdaoyzbx/ymir-executor:yolov5-cu111-base

# fix font download directory
ENV YOLOV5_CONFIG_DIR='/app/data'

COPY . /app
RUN mv /app/ymir/img-man/*.yaml /img-man && mkdir -p ${YOLOV5_CONFIG_DIR} && mv /app/ymir/*.ttf ${YOLOV5_CONFIG_DIR}
RUN pip uninstall -y ymir_exc && pip install "git+https://github.com/yzbx/ymir-executor-sdk.git@ymir2.1.0" && pip install -r /app/requirements.txt

RUN echo "python3 /app/ymir/start.py" > /usr/bin/start.sh
CMD bash /usr/bin/start.sh
