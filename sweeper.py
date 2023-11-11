'''
MINESWEEPER
Böök Enna-Liina

Kentän merkinnät:
tyhjä = avaamaton turvallinen
x = avaamaton miina
0 = turvallinen
M = miina
'''

import sys
import random
import time
import datetime
import pyglet
import haravasto
import history

SPRITEPX = 40 #sprite-kuvakkeiden resoluutio

tila = {
    "kentta": [],
    "pelitila": "v1",   #v1, v2 = päävalikon ruutuja, k = kuolema, w = voitto, p = pelissä
    "leveys": 20,
    "korkeus": 15,
    "miinat": 10,
    "sekunnit": 0,
    "minuutit": 0,
    "siirrot": 0,
    "haviodata": 0,
    "voittodata": 0
}

def laske_miinat(x, y, kentta):
    """
    Laskee annetun ruudun ympärillä olevat miinat.
    Myös itse ruudussa oleva miina lasketaan.
    
    x,y: ruudun sijainti kentällä
    kentta: ruudun kenttä
    """
    
    miinat = 0
    
    for i, ruutu in enumerate(kentta):
        for j, sisalto in enumerate(ruutu):
            if i in (y, y - 1, y + 1):
                if j in (x, x - 1, x + 1):
                    if sisalto in ("xf", "x"):
                        miinat = miinat + 1
    
    return miinat

def tulvataytto(planeetta, x, y):
    """
    Merkitsee planeetalla olevat tuntemattomat ruudut turvalliseksi siten, että
    täyttö aloitetaan annetusta x, y -pisteestä.
    
    planeetta: ruutujen kenttä
    x,y: pisteen sijainti kentällä
    """
    
    numero_merkit = ["1","2","3","4","5","6","7","8","9"]
    
    miinat_vieressa = laske_miinat(x, y, planeetta)
    
    if miinat_vieressa > 0:
        merkki = str(miinat_vieressa)
        planeetta[y][x] = merkki
        return
    elif planeetta[y][x] in ("x", "0") or planeetta[y][x] in numero_merkit:
        return
    else:
        pisteet = [(x, y)]
        while pisteet:
            pari = pisteet.pop()
            planeetta[pari[1]][pari[0]] = "0"
            for i, ruutu in enumerate(planeetta):
                for j, sisalto in enumerate(ruutu):
                    if i in (y, y - 1, y + 1) and j in (x - 1, x + 1) and sisalto == " ":
                    #tämä ja seuraava elif-lause välttävät aloitusruudun tutkimista
                        miinat_vieressa = laske_miinat(j, i, planeetta)
                        if miinat_vieressa > 0:
                            tulvataytto(planeetta, j, i)
                        else:
                            pisteet.append([j, i])
                            tulvataytto(planeetta, j, i)
                    elif i in (y - 1, y + 1) and j in (x, x - 1, x + 1) and sisalto == " ":
                        miinat_vieressa = laske_miinat(j, i, planeetta)
                        if miinat_vieressa > 0:
                            tulvataytto(planeetta, j, i)
                            return
                        else:
                            pisteet.append([j, i])
                            tulvataytto(planeetta, j, i)

def hiiri_kasittelija(x, y, nappi, _):
    """
    Hiirikäsittelijä pelitiloille joissa peli on käynnissä.
    
    x, y: hiiren koordinaatit nappia painaessa
    nappi: painettu nappi
    """
    
    for i, rivi in enumerate(tila["kentta"]):
        for j, _ in enumerate(rivi):
            if tila["pelitila"] == "p":
                
                y_rajat = i * SPRITEPX <= y <= i * SPRITEPX + SPRITEPX
                x_rajat = j * SPRITEPX <= x <= j * SPRITEPX + SPRITEPX
                
                if y_rajat and x_rajat:
                    tyyppi = tila["kentta"][i][j]
                    if nappi == haravasto.HIIRI_VASEN:
                        if tyyppi == " ":
                            tulvataytto(tila["kentta"], j, i)
                            tila["siirrot"] = tila["siirrot"] + 1
                        elif tyyppi == "x":
                            tila["kentta"][i][j] = "M"
                            tila["siirrot"] = tila["siirrot"] + 1
                            tila["pelitila"] = "k"
                    elif nappi == haravasto.HIIRI_OIKEA:    
                        if tyyppi == "f":
                            tila["kentta"][i][j] = " "
                        elif tyyppi == "xf":
                            tila["kentta"][i][j] = "x"
                        elif tyyppi == " ":
                            tila["kentta"][i][j] = "f"
                        elif tyyppi == "x":
                            tila["kentta"][i][j] = "xf"
            elif tila["pelitila"] in ("k", "w"):
                
                reuna = tila["leveys"] * SPRITEPX
                play_y = 92 <= y <= 115
                play_x = reuna + 37 <= reuna + 182
                menu_y = 54 <= y <= 75
                menu_x = reuna + 58 <= x <= reuna + 164
                quit_y = 19 <= y <= 75
                quit_x = reuna + 58 <= x <= reuna + 164
                
                if nappi == haravasto.HIIRI_VASEN:
                    if play_y and play_x:
                        haravasto.lopeta()
                        tila["voittodata"] = 0
                        tila["haviodata"] = 0
                        tila["sekunnit"] = 0
                        tila["minuutit"] = 0
                        tila["siirrot"] = 0
                        tila["pelitila"] = "p"
                        main()
                    elif menu_y and menu_x:
                        haravasto.lopeta()
                        tila["voittodata"] = 0
                        tila["haviodata"] = 0
                        tila["sekunnit"] = 0
                        tila["minuutit"] = 0
                        tila["siirrot"] = 0
                        tila["pelitila"] = "v1"
                        main()
                    elif quit_y and quit_x:
                        haravasto.lopeta()

def hiiri_kasittelija_paavalikko(x, y, nappi, muokkausnapit):
    """
    Hiirikäsittelijä pelin päävalikolle
    
    x, y: hiiren koordinaatit nappia painaessa
    nappi: painettu nappi
    """
    
    if nappi == haravasto.HIIRI_VASEN:
        if tila["pelitila"] == "v1":
            
            quick_y = 280 <= y <= 350
            quick_x = 152 <= x <= 299
            new_y = 205 <= y <= 258
            new_x = 92 <= x <= 357
            stat_y = 130 <= y <= 183
            stat_x = 92 <= x <= 357
            quit_y = 73 <= y <= 108
            quit_x = 139 <= x <= 309
            
            if quick_y and quick_x:
                tila["leveys"] = 10
                tila["korkeus"] = 10
                tila["miinat"] = 10
                tila["pelitila"] = "p"
                haravasto.lopeta()
                main()  
            elif new_y and new_x:
                tila["pelitila"] = "v2"
            elif stat_y and stat_x:
                tila["pelitila"] = "v3"
            elif quit_y and quit_x:
                haravasto.lopeta()
        elif tila["pelitila"] == "v2":
            
            vaikeus_y = 330 <= y <= 364
            easy_x = 32 <= x <= 116
            medium_x = 139 <= x <= 309
            hard_x = 332 <= x <= 416
            width_y = 165 <= y <= 184
            length_y = 217 <= y <= 237
            mines_y = 95 <= y <= 114
            vasen_x = 250 <= x <= 269
            oikea_x = 339 <= x <= 358
            start_y = 27 <= y <= 61
            start_x = 181 <= x <= 266
            takaisin_y = 14 <= y <= 48
            takaisin_x = 17 <= x <= 51
            
            if vaikeus_y:
                if easy_x:
                    tila["leveys"] = 10
                    tila["korkeus"] = 10
                    tila["miinat"] = 5
                    tila["pelitila"] = "p"
                    haravasto.lopeta()
                    main()
                elif medium_x:
                    tila["leveys"] = 15
                    tila["korkeus"] = 15
                    tila["miinat"] = 30
                    tila["pelitila"] = "p"
                    haravasto.lopeta()
                    main()
                elif hard_x:
                    tila["leveys"] = 20
                    tila["korkeus"] = 20
                    tila["miinat"] = 100
                    tila["pelitila"] = "p"
                    haravasto.lopeta()
                    main()
            elif width_y:
                if vasen_x and tila["leveys"] != 1:
                    tila["leveys"] = tila["leveys"] - 1
                elif oikea_x:
                    tila["leveys"] = tila["leveys"] + 1
            elif length_y:
                if vasen_x and tila["korkeus"] != 1:
                    tila["korkeus"] = tila["korkeus"] - 1
                elif oikea_x:
                    tila["korkeus"] = tila["korkeus"] + 1
            elif mines_y:
                if vasen_x and tila["miinat"] != 1:
                    tila["miinat"] = tila["miinat"] - 1
                elif oikea_x:
                    tila["miinat"] = tila["miinat"] + 1
            elif start_y and start_x:
                tila["pelitila"] = "p"
                haravasto.lopeta()
                main()
            elif takaisin_y and takaisin_x:
                tila["pelitila"] = "v1"
        elif tila["pelitila"] == "v3":
            takaisinv3_y = 548 <= y <= 584
            takaisinv3_x = 13 <= x <= 48
            historia_y = 560 <= y <= 579
            historia_x = 323 <= x <= 579
            if takaisinv3_y and takaisinv3_x:
                tila["pelitila"] = "v1"
            if historia_y and historia_x:
                try:
                    history.listbox()
                except FileNotFoundError:
                    pass

def miinoita(kentta, vapaat, lkm):
    """
    Asettaa kentällä miinoja satunnaisiin paikkoihin.
    
    kentta: miinoitettava kenttä
    vapaat: lista vapaista paikoista kentällä
    lkm: asetettavien miinojen lukumäärä
    """
    
    paikat = random.sample(vapaat, lkm)
    for paikka in paikat:
        x = paikka[0]
        y = paikka[1]
        kentta[y][x] = "x"

def uusi_kentta(korkeus, leveys, miinat):
    """
    Luo uuden tyhjän kentän ja miinoittaa sen
    
    korkeus, leveys: luotavan kentän dimensiot
    miinat: kentälle asetettavien miinojen määrä
    """
    
    kentta = []
    
    for rivi in range(korkeus):
        kentta.append([])
        for sarake in range(leveys):
            kentta[-1].append(" ")
    tila["kentta"] = kentta
    
    vapaat = []
    
    for x in range(leveys):
        for y in range(korkeus):
            vapaat.append((x, y))
    miinoita(tila["kentta"], vapaat, miinat)

def piirra_kentta():
    """
    Piirtää kentän ruudut haravasto-moduulin avulla
    """
    
    leveyspx = tila["leveys"] * SPRITEPX
    korkeuspx = tila["korkeus"] * SPRITEPX
    minuutti = str(tila["minuutit"]).zfill(2)
    sekuntti = str(tila["sekunnit"]).zfill(2)
    
    if tila["pelitila"] in ("p", "k", "w"):
        haravasto.tyhjaa_ikkuna()
        haravasto.piirra_tausta()
        
        miina = "mines: {}".format(tila["miinat"])
        aika = "{}:{}".format(minuutti, sekuntti)
        siirto = "{}".format(tila["siirrot"])
        val = (225, 225, 225, 175)
        
        haravasto.piirra_tekstia(miina, leveyspx - 115, korkeuspx, koko=15, vari=val)
        haravasto.piirra_tekstia(aika, 15, korkeuspx, koko=15, vari=val)
        haravasto.piirra_tekstia(siirto, leveyspx / 2 - 10, korkeuspx, koko=15, vari=val)
        
        haravasto.aloita_ruutujen_piirto()
        for i, rivi in enumerate(tila["kentta"]):
            for j, sarake in enumerate(rivi):
                sprite_y = i * SPRITEPX
                sprite_x = j * SPRITEPX
                
                numero_merkit = ["1","2","3","4","5","6","7","8","9"]
                
                if sarake == "M":
                    haravasto.lisaa_piirrettava_ruutu("x", sprite_x, sprite_y)
                elif sarake == "0":
                    haravasto.lisaa_piirrettava_ruutu("0", sprite_x, sprite_y)
                elif sarake in ("f", "xf"):
                    haravasto.lisaa_piirrettava_ruutu("f", sprite_x, sprite_y)
                elif sarake in numero_merkit:
                    haravasto.lisaa_piirrettava_ruutu(sarake, sprite_x, sprite_y)
                elif sarake == "x":
                    haravasto.lisaa_piirrettava_ruutu(" ", sprite_x, sprite_y)
                else:
                    haravasto.lisaa_piirrettava_ruutu(" ", sprite_x, sprite_y)
        haravasto.piirra_ruudut()
        
    if tila["pelitila"] == "k":
        pyglet.clock.unschedule(ajastin)
        
        if tila["haviodata"] == 0:
            kirjoita_tilasto()
            tila["haviodata"] = 1
            #estää yhden pelin tilaston kirjoittamisen useammin kuin kerran
        
        haravasto.muuta_ikkunan_koko(SPRITEPX * tila["leveys"] + 225,SPRITEPX * tila["korkeus"] + 50)
        
        haravasto.aloita_ruutujen_piirto()
        #seuraava otettu haravastosta
        haravasto.grafiikka["spritet"].append(pyglet.sprite.Sprite(
            pyglet.resource.image("loss.png"),
            SPRITEPX * tila["leveys"],
            0,
            batch=haravasto.grafiikka["puskuri"]
        ))
        haravasto.piirra_ruudut()
        
        aika = "time was {}:{}".format(minuutti, sekuntti)
        siirto = "with {} moves used".format(tila["siirrot"])
        val = (225, 225, 225, 150)
        
        haravasto.piirra_tekstia(aika, leveyspx + 40, 150, koko=15, vari=val)
        haravasto.piirra_tekstia(siirto, leveyspx + 20, 125, koko=15, vari=val)
        
    elif tila["pelitila"] == "w":
        pyglet.clock.unschedule(ajastin)
        
        if tila["voittodata"] == 0:
            kirjoita_tilasto()
            tila["voittodata"] = 1
            
        haravasto.muuta_ikkunan_koko(leveyspx + 225,korkeuspx + 25)
        
        haravasto.aloita_ruutujen_piirto()
        haravasto.grafiikka["spritet"].append(pyglet.sprite.Sprite(
            pyglet.resource.image("win.png"),
            SPRITEPX * tila["leveys"],
            0,
            batch=haravasto.grafiikka["puskuri"]
        ))
        haravasto.piirra_ruudut()
        
        aika = "time was {}:{}".format(minuutti, sekuntti)
        siirto = "with {} moves used".format(tila["siirrot"])
        val = (225, 225, 225, 150)
        
        haravasto.piirra_tekstia(aika, leveyspx + 40, 150, koko=15, vari=val)
        haravasto.piirra_tekstia(siirto, leveyspx + 20, 125, koko=15, vari=val)
        
def piirra_paavalikko():
    """
    Piirtää ikkunan kun pelitila on päävalikossa
    """
    
    leveyspx = tila["leveys"] * SPRITEPX
    korkeuspx = tila["korkeus"] * SPRITEPX
    
    if tila["pelitila"] == "v1":    
        haravasto.tyhjaa_ikkuna()
        haravasto.piirra_tausta()
        
        haravasto.aloita_ruutujen_piirto()
        haravasto.grafiikka["spritet"].append(pyglet.sprite.Sprite(
            pyglet.resource.image("Thumbnail.png"),
            0,
            0,
            batch=haravasto.grafiikka["puskuri"]
        ))
        haravasto.piirra_ruudut()
        
    elif tila["pelitila"] == "v2":
        haravasto.tyhjaa_ikkuna()
        haravasto.piirra_tausta()
        
        haravasto.aloita_ruutujen_piirto()
        haravasto.grafiikka["spritet"].append(pyglet.sprite.Sprite(
            pyglet.resource.image("Thumbnail2.png"),
            0,
            0,
            batch=haravasto.grafiikka["puskuri"]
        ))
        haravasto.piirra_ruudut()
        
        haravasto.piirra_tekstia(str(tila["korkeus"]), 286, 212, koko=20)
        haravasto.piirra_tekstia(str(tila["leveys"]), 286, 159, koko=20)
        haravasto.piirra_tekstia(str(tila["miinat"]), 286, 89, koko=20)
        
    elif tila["pelitila"] == "v3":
        haravasto.tyhjaa_ikkuna()
        haravasto.piirra_tausta()
        
        haravasto.aloita_ruutujen_piirto()
        haravasto.grafiikka["spritet"].append(pyglet.sprite.Sprite(
            pyglet.resource.image("Thumbnail3.png"),
            0,
            0,
            batch=haravasto.grafiikka["puskuri"]
        ))
        haravasto.piirra_ruudut()
        
        selitys = "result, time, dimensions, mines, moves, date"
        har = (225, 225, 225, 50)
        val = (255, 255, 255, 150)
        
        try:
            with open("stats.txt", "r") as tiedosto:
                tiedot = tiedosto.read().split('\n')
                tiedot_uusin = list(reversed(tiedot))
                
                haravasto.piirra_tekstia(selitys, 80, korkeuspx - 85, koko=10, vari=har)
                
                for i, data in enumerate(tiedot_uusin):
                    paikka = 490 - (i - 1) * 30
                    haravasto.piirra_tekstia(str(data), 30, paikka, koko=15, vari=val)
        except FileNotFoundError:
            haravasto.piirra_tekstia(selitys, 80, korkeuspx - 85, koko=10, vari=har)
            haravasto.piirra_tekstia("NO PLAYED GAMES FOUND", 30, 460, koko=15, vari=val)
               
def laske_avatut():
    """
    Laskee kentällä olevat avatut ruudut
    """
    
    auki = 0
    
    numero_merkit = ["1","2","3","4","5","6","7","8","9"]
    
    for sarake in tila["kentta"]:
        for ruutu in sarake:
            if ruutu == "0" or ruutu in numero_merkit:
                auki = auki + 1
    return auki

def tarkista_voitto(_):
    """
    Toistuva käsittelijä joka tarkistaa onko pelaaja voittanut
    """
    
    turvalliset = tila["leveys"] * tila["korkeus"] - tila["miinat"]
    avatut = laske_avatut()
    
    if turvalliset == avatut:
        tila["pelitila"] = "w"

def ajastin(_):
    """
    Toistuva käsittelijä pelin ajastimelle
    """
    
    tila["sekunnit"] = tila["sekunnit"] + 1
    
    if tila["sekunnit"] == 60:
        tila["minuutit"] = tila["minuutit"] + 1
        tila["sekunnit"] = 0

def paavalikko():
    """
    Luo päävalikon ja asettaa sen käsittelijät
    """
    
    haravasto.luo_ikkuna(450, 600)
    haravasto.aseta_hiiri_kasittelija(hiiri_kasittelija_paavalikko)
    haravasto.aseta_piirto_kasittelija(piirra_paavalikko)

def kirjoita_tilasto():
    """
    Kirjoittaa pelin tiedot voiton tai häviön jälkeen tekstitiedostoon.
    
    Tiedoston nimi on stats.txt, ja se luodaan tarvittaessa
    """
    
    with open("stats.txt", "a+") as tiedosto:
        
        if tila["pelitila"] == "k":
            tulos = "LOSS"
        elif tila["pelitila"] == "w":
            tulos = "WIN"
        
        sek = str(tila["sekunnit"])
        min = str(tila["minuutit"])
        aika = "{}:{}".format(min.zfill(2), sek.zfill(2))
        koko = "{}x{}".format(str(tila["leveys"]), str(tila["korkeus"]))
        miinat = str(tila["miinat"])
        siirrot = str(tila["siirrot"])
        pvm = datetime.datetime.now().strftime("%d-%m-%Y")
        
        tilasto = "{}, {}, {}, {}, {}, {}\n".format(tulos, aika, koko, miinat, siirrot, pvm)
        
        tiedosto.write(tilasto)
        tiedosto.close()

def main():
    
    sys.setrecursionlimit(10000)
    
    uusi_kentta(tila["korkeus"], tila["leveys"], tila["miinat"])
    
    haravasto.lataa_kuvat("spritet")
    
    if tila["pelitila"] in ("v1", "v2"):
        paavalikko()
    elif tila["pelitila"] == "p":
        haravasto.luo_ikkuna(SPRITEPX * tila["leveys"],SPRITEPX * tila["korkeus"] + 25, taustavari=(70, 55, 105, 225))
        haravasto.aseta_hiiri_kasittelija(hiiri_kasittelija)
        haravasto.aseta_piirto_kasittelija(piirra_kentta)
        haravasto.aseta_toistuva_kasittelija(ajastin, 1)
        haravasto.aseta_toistuva_kasittelija(tarkista_voitto)
    
    haravasto.aloita()

if __name__ == "__main__":
    main()