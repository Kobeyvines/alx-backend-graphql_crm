
# CRM Celery & Report Setup

  

This guide explains how to set up Redis, Celery, and Celery Beat to generate weekly CRM reports.

  

---

  

## 1. Install Redis

```bash

sudo  apt  install  redis-server

  

Verify  Redis  is  running:

  

redis-cli  ping

# should return: PONG

  

2.  Install  Python  Dependencies

  

pip  install  -r  requirements.txt

  

Dependencies  include:

  

celery[redis]

  

django-celery-beat

  

redis

  

requests

  

3.  Run  Migrations

  

python  manage.py  migrate

  

4.  Configure  Celery  in  Django

  

In  crm/settings.py,  make  sure  the  following  is  included:

  

INSTALLED_APPS  = [

# other apps...

"django_celery_beat",

]

  

from  celery.schedules  import  crontab

  

CELERY_BEAT_SCHEDULE  =  {

'generate-crm-report':  {

'task':  'crm.tasks.generate_crm_report',

'schedule':  crontab(day_of_week='mon', hour=6, minute=0),

},

}

  

5.  Start  Celery  Worker

  

celery  -A  crm  worker  -l  info

  

6.  Start  Celery  Beat

  

celery  -A  crm  beat  -l  info

  

Celery  Beat  will  schedule  the  generate_crm_report  task  every  Monday  at  6:00  AM.

7.  Verify  Logs

  

Reports  are  written  to:

  

/tmp/crm_report_log.txt

  

Each  entry  follows  the  format:

  

YYYY-MM-DD  HH:MM:SS  -  Report:  X  customers,  Y  orders,  Z  revenue

  

If  the  task  fails,  the  error  will  also  be  logged  in  the  same  file.

  
  

---

  

✅  This  single  README  now  includes:

-  Redis  install  instructions

-  Python  dependencies  install

-  Database  migrations

-  Celery  +  Celery  Beat  setup

-  Required  snippet  for  `crm/settings.py`

-  Worker & Beat  commands

-  Log  verification

  

---

  

Do  you  want  me  to  also  include  an  example  of  the  **expected  log  entry**  with  dummy  values (e.g.
