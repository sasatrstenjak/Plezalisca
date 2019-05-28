#!/usr/local/bin/python3
# encoding=utf-8
#zajem podatkov
# import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


#plezalisca po drzavah
website_url = requests.get('http://www.plezanje.net/climbing/db/countryIntro.asp?otype=C').text
soup = BeautifulSoup(website_url, "html.parser")
my_table = soup.find("table",{"class":"fmtTable"})
linki_drzave = my_table.findAll('a')
drzave = []
for podatek in linki_drzave:
    drzave.append([podatek.text,podatek['href']])

with open('drzave.csv','a',encoding='utf8') as f:
    f.write("")
    f.close()

for drzava,link_dr in drzave:

    print(drzava)
    # Stran s seznamom slo plezalisc
    website_url = requests.get('http://www.plezanje.net/climbing/db/' + link_dr).text
    # Tabela plezalisc
    soup = BeautifulSoup(website_url, "html.parser")
    MyTable = soup.find("table",{"class":"fmtTable"})
    # Imena plezalisc in povezave do posazmenih:
    links = MyTable.findAll('a')
    seznam_pl = [link.next for link in links]
    #print(seznam_pl)

    # Podatki o stevilu smeri in tezavnosti (iz tabele o vseh slo plezaliscih)
    info = MyTable.findAll("td", {"style":"text-align: center"})
    st_smeri = info[::2]
    tezavnosti = info[1::2]
    #print(st_smeri)

    # Koncni slovar plezalisc
    vsa_plezalisca = {}
    #with open('drzave.csv','a',encoding='utf8') as f:
    for pl in seznam_pl:
    #        f.write(drzava + ',' + pl.replace('\'','') + '\n')
        vsa_plezalisca[pl] = {}
    #    f.close()
    
    with open("plezalisca.csv","a",encoding='utf8') as f:
        for i in range(len(seznam_pl)):
            ime_pl = seznam_pl[i]
            #print(ime_pl)
            vsa_plezalisca[ime_pl]["link"] = links[i]["href"]       # V koncni slovar dodamo link
            if st_smeri[i].text == '':
                vsa_plezalisca[ime_pl]["stevilo_smeri"] = 0
            else:
                vsa_plezalisca[ime_pl]["stevilo_smeri"] = int(st_smeri[i].text)
            skupna_tez = tezavnosti[i].text
            #print(skupna_tez.split(" "))
            if len(skupna_tez.split(" ")) == 3:
                najlazja = skupna_tez.split(" ")[0]
                najtezja = skupna_tez.split(" ")[2]
            else:
                najlazja = skupna_tez.split(" ")[0]
                najtezja = skupna_tez.split(" ")[0]
            vsa_plezalisca[ime_pl]["razpon_tezavnosti"] = skupna_tez
            vsa_plezalisca[ime_pl]["najlazja_smer"] = najlazja
            vsa_plezalisca[ime_pl]["najtezja_smer"] = najtezja
            f.write(ime_pl + "," + drzava + "," + st_smeri[i].text + "," + skupna_tez + "," + najlazja + "," + najtezja + "\n" )
        f.close()

    
    for plezalisce in seznam_pl:
        with open("regije.csv","a",encoding="utf8") as f:
            print(plezalisce)
            # Url za posamezno plezalisce
            url_pl = requests.get("http://www.plezanje.net/climbing/db/" + vsa_plezalisca[plezalisce]["link"]).text
            soup = BeautifulSoup(url_pl, "html.parser")
            regija_ref = soup.find("div", {"id":"breadcrumbs"})
            for x in regija_ref.findAll("a"):
                if x["href"][:8] == "showArea":
                    regija = x.text
                else:
                    regija = None
            # Tabela smeri na plezaliscu
            new_table = soup.find("table",{"class":"fmtTable"})
            f.write(plezalisce.replace("\'","") + "," + str(regija) + "," + drzava + "\n")
            #print(new_table)
            smeri = []
            tezavnosti = []
            dolzine = []
            # Naredimo seznam vseh imen smeri skupaj s tezavnostmi za to plezalisce
            #print(new_table)
            f.close()
        with open("smeri.csv","a",encoding='utf8') as f:
            if new_table is not None:
                for smer in new_table.findAll("tr"):
                    ime_smeri = smer.find("a")
                    if ime_smeri is not None:
                        ime_smeri = ime_smeri.text
                        smeri.append(ime_smeri)
                        f.write(ime_smeri  + "," +plezalisce )

                        tez_smeri = smer.find("p",{"class":None})
                        if tez_smeri is not None:
                            tez_smeri = tez_smeri.text
                        tezavnosti.append(tez_smeri)
                        f.write(","  + tez_smeri)
                        

                        dol_smeri = smer.find("td",{"class":"right"})
                        if dol_smeri is not None:
                            dol_smeri = dol_smeri.text
                        else:
                            dol_smeri = str(None)
                        dolzine.append(dol_smeri)
                        f.write("," + dol_smeri)
                        f.write("\n")

                    #f.write(ime_smeri.text + "," + plezalisce + "," + tez_smeri + "," + dol_smeri + "\n")
                '''
                smeri_plezalisce = []
                for i in range(len(smeri)):
                    if len(tezavnosti) < len(smeri):
                        tezavnosti.append([None]*(len(smeri)-len(tezavnosti)))
                    if len(dolzine) < len(smeri):
                        dolzine.append([None]*(len(smeri)-len(dolzine)))
                    smeri_plezalisce.append([smeri[i],tezavnosti[i],dolzine[i]])

                vsa_plezalisca[plezalisce]["smeri"] = smeri_plezalisce
                '''
        f.close()
    #print(vsa_plezalisca)
    

#df = pd.DataFrame()
#df["Plezalisce"] = plezalisca
#print df
#print plezalisca
