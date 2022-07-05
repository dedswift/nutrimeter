# Mask R-CNN Image (micro service)

FROM python:3.7.13


RUN apt-get update && apt-get install -y git
RUN pip install --upgrade pip

WORKDIR /food-recognizer-tools

# Download AI crowd helper classes to parse COCO annotations
RUN git clone https://gitlab.aicrowd.com/nikhil_rayaprolu/food-recognition/

WORKDIR /food-recognizer-tools/food-recognition/

# Install Mask R-CNN dependencies
RUN pip install 'h5py==2.10.0'\
    protobuf==3.20.*\
    pandas\
    matplotlib\
    scikit-image==0.16.2\
    cython\
    "tensorflow==1.15.0"\
    "tensorflow-gpu==1.15.0"\
    "keras==2.1.6"\
    scipy\
    imgaug\
    pillow\
    "tqdm==4.19.9"

RUN pip install git+https://github.com/AIcrowd/coco.git#subdirectory=PythonAPI
# RUN pip install -r requirements.txt

# Setup Mask R-CNN packages
RUN python setup.py install

# Open CV dependencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Mask R-CNN flask API
RUN pip install Flask

# JSON serialization
RUN pip install jsonpickle
RUN pip install ipython

WORKDIR /food-recognizer

# Copy source code and model weights to container
# COPY . .

# Instead of running /bin/python as the default command for the container
# override with bash for testing/debugging
# CMD [ "/bin/bash" ]

# Run this when deploying
CMD [ "python", "./app.py" ]
