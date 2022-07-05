FROM python

RUN pip3 install Flask==2.1.2
RUN pip3 install click==8.1.3
RUN pip3 install itsdangerous==2.1.2
RUN pip3 install Jinja2==3.1.2
RUN pip3 install MarkupSafe==2.1.1
RUN pip3 install Werkzeug==2.1.2
RUN pip3 install requests==2.27.1
RUN pip3 install firebase-admin==5.2.0
WORKDIR /nutrimeter
# CMD [ "/bin/bash" ]
CMD ["python", "./server/FoodAPI/app.py"]
