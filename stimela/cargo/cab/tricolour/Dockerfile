FROM stimela/tricolour:1.2.5
MAINTAINER <sphemakh@gmail.com>
ADD src /scratch/code
ENV LOGFILE ${OUTPUT}/logfile.txt
RUN rm /usr/bin/python
RUN ln /usr/bin/python3 /usr/bin/python
CMD /scratch/code/run.sh
