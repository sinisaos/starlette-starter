Example of [Starlette](https://www.starlette.io/) and [Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/)   starter aplication with users managment and auth (thanks to [@ceyzaguirre4](https://github.com/ceyzaguirre4))

Open terminal and run:

```shell
virtualenv -p python3 envname
cd envname
source bin/activate
git clone https://github.com/sinisaos/starlette-starter.git
cd starlette-starter
pip install -r requirements.txt
sudo -i -u yourpostgresusername psql
CREATE DATABASE starter;
\q
touch .env
## put this two line in .env file
## DB_URI="postgres://username:password@localhost:5432/starter"
## SECRET_KEY="your secret key"
uvicorn app:app --port 8000 --host 0.0.0.0 
```

Change line 22 in accounts models.py to set register user as admin user.