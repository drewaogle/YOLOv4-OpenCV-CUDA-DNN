FROM aperturedata/aperturedb-notebook

ADD setup_and_start.sh /
COPY notebooks /notebooks

EXPOSE 8888
CMD ["/setup_and_start.sh"]

