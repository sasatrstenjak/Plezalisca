#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *
#import bottle
import hashlib

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

# Skrivnost za kodiranje cookijev
secret = "to skrivnost je zelo tezko uganiti 1094107c907cw982982c42"

# odkomentiraj, če želiš sporočila o napakah
debug(True)

######################################################################
# Pomožne funkcije

def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

@get("/plezalisca/")
def vrni_plezalisca():
    """Seznam plezalisc"""
    
    cur.execute("SELECT ime,drzava,st_smeri,razpon_ocen FROM plezalisca")
    
    return template('plezalisca.html', plezalisce=cur)


@get("/drzave/")
def vrni_drzave():
    """Seznam po drzavah"""
    
    cur.execute("SELECT drzava,plezalisce FROM regije")
    
    return template('drzave.html', drzave=cur)

@get("/smeri/")
def vrni_smeri():
    """Seznam vseh smeri"""
    
    cur.execute("SELECT ime,plezalisce,ocena,dolzina FROM smeri")
    
    return template('smeri.html', smeri=cur)


@get("/")
def main():
    """Začetna stran"""

    return template("zacetna.html")




######################################################################
# Glavni program

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8000/
run(host='localhost', port=8000)
