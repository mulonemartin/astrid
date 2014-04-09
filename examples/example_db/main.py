#!/usr/bin/env python
# -*- coding: utf-8 -*-

#You don't have to do this two lines if you are using in production trought pypi.
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

"""

Requirements:
        a) MySQLdb (easy_install mysqldb)
        b) Mako templates (easy_install Mako )


Test on connection to mysql db using mysqldb connector

1) CREATE DB AND USERS

mysql> create database test1;
Query OK, 1 row affected (0.00 sec)

mysql> CREATE USER 'testuser'@'localhost' IDENTIFIED BY 'blabla';
Query OK, 0 rows affected (0.00 sec)

mysql> GRANT ALL ON test1.* to 'testuser'@'%';
Query OK, 0 rows affected (0.00 sec)

2) CREATE TABLES

 CREATE TABLE `table1` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  `lastname` varchar(50) NOT NULL,
  `tel` varchar(50),
  PRIMARY KEY  (`id`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;


"""

import MySQLdb
import MySQLdb.cursors

# Astrid imports
from astrid.web.wrapper import ContextManager


from astrid.web.wsgi import WSGIApplication
from astrid.http.server import run
from astrid.web.expose import expose
from astrid.http.response import HTTPError, HTTPRedirect


options = {
        'SERVER': 'wsgiref',
        'IP': '0.0.0.0',
        'PORT': 8000,
        'TEMPLATES_FOLDER': 'templates/',
        'STATIC_FOLDER': os.path.abspath('../static'),
        'DB': 'mysql://testuser:blabla@localhost:3306/test1'
    }


class ConnectorMysqldb(ContextManager):
    def __init__(self):

        self.db = None
        self.name = 'ConnectionMysqldb'
        self.uri = options['DB']

        uri_list = self.uri.split('://')[1].split(':')
        self.user = uri_list[0]
        self.passw = uri_list[1].split('@')[0]
        self.host = uri_list[1].split('@')[1]
        self.port = uri_list[2].split('/')[0]
        self.dbname = uri_list[2].split('/')[1]

    def connect(self):
        """Connect to db"""
        self.db = MySQLdb.connect(self.host, self.user, self.passw, self.dbname,
                                  cursorclass=MySQLdb.cursors.DictCursor,
                                  use_unicode=True, charset='utf8', init_command='SET NAMES UTF8')

    def on_start(self):
        """On start"""
        self.connect()

    def on_success(self):
        """On success"""
        self.db.commit()
        self.db.close()

    def on_failure(self):
        """On fail"""
        self.db.rollback()

        try:

            self.db.close()
        except:
            pass

connector_mysql = ConnectorMysqldb()


@expose(template='index.html')
def test_no_connect():
    message = "This is a test, no connection to any db"
    return dict(message=message)


@expose(template='index.html', contexts=[connector_mysql])
def test_connect_only():
    message = "This is a test, only connection to db"
    return dict(message=message)


@expose(template='index.html', contexts=[connector_mysql])
def insert_row():

    cur = connector_mysql.db.cursor()
    cur.execute('insert into table1 (name, lastname, tel) values (%s, %s, %s)', ('John', 'Karl', '12-122121'))

    message = "Row inserted"
    return message





if __name__ == '__main__':

    app = WSGIApplication(options)
    run(app, server=options['SERVER'], host=options['IP'], port=options['PORT'])

