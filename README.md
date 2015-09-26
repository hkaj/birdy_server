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

**Instructions to use in production:**

The previous instructions are sufficient for a development environment. To run the application in production though, setting up a Gunicorn server and an NginX reverse proxy is recommended. The easiest way to do so is to install Gunicorn, NginX, and then to follow the part of [this DigitalOcean documentation](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-14-04) relative to the NginX configuration. The only requirement is to setup the proxy pass like this:
```
    location / {
        proxy_pass         http://127.0.0.1:8000/;
    }
```
Once it's done, run:

```bash
# echo "alias brdy='cd /home/birdy/birdy_server && source venv/bin/activate && gunicorn -w 3 --log-file /var/log/gunicorn/error.log --access-logfile /var/log/gunicorn/access.log -b localhost:8000 birdy_server:app &'" >> ~/.bashrc && mkdir -p /var/log/gunicorn && touch /var/log/gunicorn/access.log && touch /var/log/gunicorn/error.log
```

This will setup an alias for your root user to start 3 Gunicorn workers serving the application on port 8000, which is queried by NginX thanks to the `proxy_pass` mentionned above.

Now typing `brdy` as root will start the application, and `killall gunicorn` will stop it.

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
