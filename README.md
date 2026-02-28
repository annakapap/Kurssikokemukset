# Kurssikokemukset
Kurssikokemuksia keräävä alusta.

**Sovelluksen toiminnot**
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan ilmoituksia käymistään kursseista, niiden sisällöstä ja kokemuksistaan.
- Käyttäjä näkee sovellukseen lisätyt ilmoitukset.
- Käyttäjä pystyy etsimään ilmoituksia hakusanalla.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät ilmoitukset.
- Käyttäjä pystyy valitsemaan ilmoitukselle yhden tai useamman luokittelun (esim. tiedekunta, aine, taso).
- Käyttäjä pystyy lisäämään lisähuomioita/täsmennyksiä omiin ja muiden käyttäjien ilmoituksiin.


## Käynnistysohjeet

Terminaalissa:

   git clone https://github.com/annakapap/Kurssikokemukset.git
   
   cd Kurssikokemukset
   
   python3 -m venv venv
   
   source venv/bin/activate
   
   pip install flask
   
   flask --app app init-db
   
   flask --app app run

Avaa selaimessa
   http://127.0.0.1:5000/


**## Testaus suurella datamäärällä**

Sovelluksen toimintaa on testattu suurella tietomäärällä käyttäen seed.py -skripitiä. Testidatassa käyttäjiä oli 200, kurssikokemuksia 20000 ja kommentteja 50000, ja kokemusten sekä kommenttien sisältö koostui neutraaleista merkkijonoista.

Tietokanta luotiin uudelleen ja data generoitiin komennolla python3 seed.py --users 200 --experiences 20000 --comments 50000, jonka jälkeen sovellus käynnistetiin komennolla flask run. Sivujen lataus pysyi nopeana suurella tietomäärällä, ja toisessa terminaalissa ajettu komento 

time curl -s "http://127.0.0.1:5000/experiences?page=50" > /dev/null
time curl -s "http://127.0.0.1:5000/experiences?q=12345&page=3" > /dev/null

tulosti

              real	0m0.010s
              user	0m0.004s
               sys	0m0.004s

              real	0m0.011s
              user	0m0.002s
               sys	0m0.006s

jolloin voidaan sanoa, että suorituskyky pysyy hyvänä myös suurella määrällä dataa.



