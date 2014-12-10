Birdy_server
============

The server part of Birdy


## Installation steps

- Create a virtualenv and activate it
- pip install -r requirements.txt in it
- Install a postgresql server
- Create a postgresql 'birdy_admin' user, and give him the rights on 'postgres' DB
- Run "./utils/db_utils.py --action init" in the birdy_server folder to initialize the DB
- Launch birdy_server.py (chmod +x and ./birdy_server.py)
- Enjoy!

## Debugging
- If the SQL stuff fail, maybe your PostgreSQL installation isn't configured to accept password login for local user. Consider switching the method in pg_hba.conf for local connection to md5 or fiddling with psycopg2.

## Tests
- Manual tests are done with curl, unit tests are coming as soon as possible.
