FROM python:3.7.13


RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential \
    bzip2 \
    cmake \
    curl \
    git \
    g++ \
    libboost-all-dev \
    pkg-config \
    rsync \
    software-properties-common \
    sudo \
    tar \
    timidity \
    unzip \
    wget \
    locales \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libgl1-mesa-glx \
    vim \
    nano


RUN apt-get install locales


RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LC_ALL en_US.UTF-8 
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  



ENV USER_NAME omarmostafa
ENV HOME_DIR /home/$USER_NAME


ENV HOST_UID 1000
ENV HOST_GID 1000


WORKDIR $HOME_DIR/food-recognition

RUN git clone https://gitlab.aicrowd.com/nikhil_rayaprolu/food-recognition/

WORKDIR $HOME_DIR/food-recognition/food-recognition

RUN pip install 'h5py==2.10.0' cython notebook && pip install -r requirements.txt

RUN python setup.py install

RUN pip install protobuf==3.20.* pandas scikit-image==0.16.2


RUN export uid=${HOST_UID} gid=${HOST_GID} && \
    mkdir -p ${HOME_DIR} && \
    echo "$USER_NAME:x:${uid}:${gid}:$USER_NAME,,,:$HOME_DIR:/bin/bash" >> /etc/passwd && \
    echo "$USER_NAME:x:${uid}:" >> /etc/group && \
    echo "$USER_NAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER_NAME && \
    chmod 0440 /etc/sudoers.d/$USER_NAME && \
    chown ${uid}:${gid} -R ${HOME_DIR}


RUN echo 'root:password' | chpasswd

USER ${USER_NAME}
WORKDIR ${HOME_DIR}

CMD [ "/bin/bash" ]

# COPY --chown=1000:1000 . .