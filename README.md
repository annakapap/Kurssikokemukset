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

