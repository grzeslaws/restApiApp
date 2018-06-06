rest api app


pip install PyJWT
pip install mysqlclient

(The problem arises if you have JWT and PyJWT installed. When doing import jwt it is importing the library JWT as opposed to PyJWT. The one you want for encoding. I did pip uninstall JWT and pip uninstall PyJWT then finally pip install PyJWT. After that it imported the correct module and generated the token! :))