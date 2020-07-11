# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

from celery.schedules import crontab
import os
from . import *

SECRET_KEY="wdwdewd"
REDIS_URL = os.environ.get('REDIS_URL','redis://localhost:6379/3')

# celery
CACHE_URL_DEFAULT= os.environ.get('CELERY_BROKER_URL')
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = os.environ.get('CELERY_TIMEZONE') or 'utc'

# sqlalchemy
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI','mysql+pymysql://root:a828215369@localhost:3306/restaurant')
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS',True)

LOG_FILE_PATH = os.environ.get('LOG_FILE_PATH') or 'tripadvisor.log'
ERROR_LOG_FILE_PATH = os.environ.get('ERROR_LOG_FILE_PATH') or 'error.log'

IMAGR_CODE_REDIS_EXPRIES = 180
LOGIN_ERROR_MAX_TIMES = 5
LOGIN_ERROR_FORBID_TIME = 600 
AREA_INFO_REDIS_CACHE_EXPIRES =7200
COMMENT_PER_ITEM=20
RESTAURANT_LIST_PAGE = 3600