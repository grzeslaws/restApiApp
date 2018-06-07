# Rest api app from flask

* init virtual environment `virtualenv venv`
* activate virtual environment `source venv/bin/activate`
* install all dependencies via pip `pip install -r requirements.txt`
* run app `python app.py`
* stop app `ctrl + z`
* deactivate virtual environment `deactivate`

###### Sometimes you need install following:
* `pip install PyJWT`
* `pip install mysqlclient`

> (The problem arises if you have JWT and PyJWT installed. When doing import jwt it is importing the library JWT as opposed to PyJWT. The one you want for encoding. I did pip uninstall JWT and pip uninstall PyJWT then finally pip install PyJWT. After that it imported the correct module and generated the token! :))