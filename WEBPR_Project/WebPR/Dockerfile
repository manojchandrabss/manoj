FROM ssci/base 
### Documentation for the image: 
### https://gitblit.saritasa.com/tree/?f=centos7-python343-nginx-uwsgi&r=saritasa/docker/images.git&h=development

RUN yum install libffi-devel -y
RUN yum install gcc


### install python 3.4.3

RUN yum install -y epel-release


RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm

#Once IUS is finished installing, we can install the most recent version of Python, which, at the time of writing, is Python 3.5.2:

RUN yum -y install python35u-*

RUN yum -y install python35u-pip

ENV APP_ENV development
ENV DJANGO_SETTINGS_MODULE config.settings.development

RUN mkdir -p /var/log/uwsgi
RUN mkdir -p /home/www/app

### for enabling ipython auto-indent feature
RUN yum install ncurses-devel -y
RUN pip3.5 install readline


### Add config files to container
ADD .docker /tmp/docker

# Add an entry-point
RUN fromdos /tmp/docker/start.sh
RUN cp /tmp/docker/start.sh /home/www
RUN chmod +x /home/www/start.sh

### Install dependencies
COPY requirements /home/www/app/requirements
RUN pip3.4 install -r /home/www/app/requirements/development.txt

WORKDIR /home/www/app

### Run our container
ENTRYPOINT []
CMD ["bash", "/home/www/start.sh"]

### Add source code to container
ADD . /home/www/app/


