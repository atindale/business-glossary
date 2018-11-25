[![Build Status](https://travis-ci.org/atindale/business-glossary.svg?branch=master)](https://travis-ci.org/atindale/business-glossary)
[![Coverage Status](https://coveralls.io/repos/github/atindale/business-glossary/badge.svg?branch=master)](https://coveralls.io/github/atindale/business-glossary?branch=master)

# Business Glossary

A simple business glossary to store and disseminate business taxonomy and vocabulary.

## Running the Application

```
git clone https://github.com/atindale/business-glossary.git
cd business-glossary
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
python create_db.py
flask run
```

## Setup

Running the above commands will create an application using the development configuration by default. This uses an SQLite database named glossary_dev.db.

You can also define two environment variables to control the configuration and database it should use.

```
export BG_DATABASE_URL=mysql://username:password@localhost/db_name
export BG_CONFIG=test
flask run
```

## Managing Users

To add a user to the glossary, us the following command. You will be prompted for a password.

```
flask users create --active user@example.com
```

A user can be assigned a role can be created like so:

```
flask roles add admin@example.com admin
```

You can remove a role from a user with:

```
flask roles remove admin@example.com admin
```

You can deactivate a user like this:

```
flask users deactivate jamestindale@outlook.com
```

The user can be activated again with this command:

```
flask users activate jamestindale@outlook.com
```

## Printing to PDF

To print glossary information to PDF `wkhtmltopdf` should be installed and available in your PATH. If it is not in the path it will be searched for at `C:\Program Files\wkhtmltopdf\bin`.

The generated PDF documents are placed in a directory named `bg_interface` that is created alongside the application directory. So if the Business Glossary is installed under `/srv/business-glossary` the generated PDFs will be created at `/src/bg_interface`.


Copyright 2016-2018 Alan Tindale
