Birdy_server
============

The server part of Birdy


## Installation steps

- Create a virtualenv and activate it
- pip install -r requirements.txt in it
- Install a postgresql server
- Create a postgresql 'birdy_admin' user, and give him the rights on 'postgres' DB
- Create 2 environment variables: *BIRDY_SETTINGS* which should point to your birdy.cfg, and *BIRDY* which should point to the folder of the server
- Run "./utils/db_utils.py --action init" in the birdy_server folder to initialize the DB
- Launch birdy_server.py (chmod +x and ./birdy_server.py)
- Enjoy!

## Settings

birdy.cfg should be organized this way:
```
SECRET_KEY = 'yourKey'

DATABASE = 'postgres'

USER = 'your_db_user'

PASSWORD = 'password'
```
## Debugging
- If the SQL stuff fail, maybe your PostgreSQL installation isn't configured to accept password login for local user. Consider switching the method in pg_hba.conf for local connection to md5 or fiddling with psycopg2.
