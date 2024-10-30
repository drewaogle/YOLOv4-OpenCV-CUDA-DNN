FROM aperturedata/aperturedb-community
RUN apt update
RUN apt install -y  python3-pip
RUN pip install aperturedb

ADD add_users.sh /
ADD start.sh /
ADD add_user.py /
ADD health_and_users.sh /

CMD ["/start.sh"]
#ENTRYPOINT /start.sh
