Example of [Starlette](https://www.starlette.io/) starter aplication with users managment and auth (thanks to [@ceyzaguirre4](https://github.com/ceyzaguirre4))

Open terminal and run:

```shell
virtualenv -p python3 envname
cd envname
source bin/activate
git clone https://github.com/sinisaos/starlette-starter.git
cd starlette-starter
pip install -r requirements.txt
mysql -u root -p
CREATE DATABASE test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
touch .env
## put this two line in .env file
## DB_URI="mysql+pymysql://username:password@localhost/test"
## SECRET_KEY="secret key"
cd src
python app.py

```
Change line 22 in tables.py and change line 47 in base.html to set register user as admin user.

