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

def get_user():
    """Poglej cookie in ugotovi, kdo je prijavljeni uporabnik,
       vrni njegov username in ime. Če ni prijavljen, presumeri
       na stran za prijavo ali vrni None (advisno od auto_login).
    """
    # Dobimo username iz piškotka
    username = request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        
        cur.execute("SELECT username FROM uporabnik WHERE username=%s", [username])
        r = cur.fetchone()
        if r is not None:
            # uporabnik obstaja, vrnemo njegove podatke
            return username
    # Če pridemo do sem, uporabnik ni prijavljen, naredimo redirect
    else:
        return None

@get("/login/")
def login_get():
    """Serviraj formo za login."""
    return template("login.html",
                           napaka=None,
                           username=None)

@post("/login/")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = request.forms.username
    # Izračunamo MD5 has gesla, ki ga bomo spravili
    password = password_md5(request.forms.password)
    print(password)
    # Preverimo, ali se je uporabnik pravilno prijavil
    cur.execute("SELECT * FROM uporabnik WHERE username=%s AND geslo=%s",
             [username, password])
    print(username)
    
    if cur.fetchone() is None:
        #print (cur.fetchone())
        # Username in geslo se ne ujemata
        username = None
        return template("login.html", napaka='Napačno geslo ali uporabniško ime.', username=username)
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")

@get("/logout/")
def logout():
    """Pobriši cookie in preusmeri na login."""
    response.delete_cookie('username')
    redirect('/login/')

@get("/register/")
def register_get():
    """Prikaži formo za registracijo."""
    return template("register.html", ime=None, priimek=None, username = None, geslo = None, napaka = None)


@post("/register/")
def register_post():
    """Registriraj novega uporabnika."""
    ime = request.forms.ime
    priimek = request.forms.priimek
    username = request.forms.username
    geslo = request.forms.password
    # Ali uporabnik že obstaja?
    c = conn.cursor()
    c.execute("SELECT * FROM uporabnik WHERE username=%s", [username])
    if c.fetchone():
        # Uporabnik že obstaja
        return template("register.html", ime=ime, priimek=priimek, username=None, napaka='To uporabniško ime je zasedeno.')
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        
        password = password_md5(geslo)
        
        c.execute("INSERT INTO uporabnik (ime, priimek, username, geslo) VALUES (%s, %s, %s, %s)",
                  (ime, priimek, username, password))
        # Daj uporabniku cookie
        response.set_cookie('username', username, path='/', secret=secret)
        return template("register.html", ime=None, priimek=None, username=None, napaka='Registracija uspešna.')
    
@get("/plezalisca/")
def plezalisca_get():
    """Seznam plezalisc"""
    username = get_user()
    cur.execute("SELECT ime,st_smeri,razpon_ocen,drzava FROM plezalisca")    
    return template('plezalisca.html', plezalisca=cur, username=username)

@post("/plezalisca/")
def plezalisca_post():
    search = request.forms.search
    username = get_user()

    if search == "":
        cur.execute("SELECT ime,st_smeri,razpon_ocen,drzava FROM plezalisca")
    else:
        cur.execute("SELECT ime,st_smeri,razpon_ocen,drzava FROM plezalisca WHERE ime = %s", [search])
        
    return template('plezalisca.html', plezalisca=cur, username=username)

@get("/drzave/")
def vrni_drzave():
    """Seznam po drzavah"""
    
    username = get_user()
    cur.execute("SELECT DISTINCT drzava FROM regije")
    
    return template('drzave.html', drzave=cur, username=username)


@get("/smeri/")
def smeri_get():
    """Seznam vseh smeri"""
    
    username = get_user()
    cur.execute("SELECT ime,plezalisce,ocena,dolzina FROM smeri")
    
    return template('smeri.html', smeri=cur, username=username)

@post("/smeri/")
def smeri_post():
    search = request.forms.search
    username = get_user()

    if search == "":
        cur.execute("SELECT ime,st_smeri,razpon_ocen,drzava FROM plezalisca")
    else:
        cur.execute("SELECT ime,st_smeri,razpon_ocen,drzava FROM plezalisca WHERE ime = %s", [search])
        
    return template('smeri.html', smeri=cur, username=username)


@get("/priljubljena/")
def vrni_priljubljena():
    """Seznam priljubljenih plezališč"""
    
    username = get_user()
    cur.execute("SELECT ime FROM priljubljena WHERE uporabnik = %s", [str(username)])
    
    return template('priljubljena.html', priljubljena=cur, username=username)

@get("/priljubljena/:plez")
def priljubljena_get(plez):

    username = get_user()
    komentar = "koko"

    cur.execute("INSERT INTO priljubljena (uporabnik, ime, komentar) VALUES (%s, %s, %s)", [str(username), plez, komentar])

    redirect("/priljubljena/")
   
    

@get('/drzave/:drz')
def po_drzavi(drz):
    username = get_user()
    cur.execute("SELECT ime,st_smeri,razpon_ocen,drzava FROM plezalisca WHERE drzava = %s", [drz])
    drzava = drz
    return template("plezalisca_drzava.html", plezalisca=cur, username=username, drzava = drzava)

@get('/plezalisca/:pl')
def po_plezaliscu(pl):
    username = get_user()
    cur.execute("SELECT ime,ocena,dolzina FROM smeri WHERE plezalisce = %s", [pl])

    return template("smeri_pl.html", smeri=cur, username=username)

@get("/")
def main():
    """Začetna stran"""
    username = get_user()
    return template("zacetna.html", username=username)


#Moznosti razvrscanja:
moznosti = [('Države po abecedi'),
            ('Ocena naraščajoče'),
            ('Ocena padajoče'),
            ('Število smeri naraščajoče'),
            ('Število smeri padajoče')]
             


######################################################################
# Glavni program

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8000/
run(host='localhost', port=8000)
