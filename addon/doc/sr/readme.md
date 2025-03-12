# Jednostavan Snimač Zvuka
Jednostavan Snimač Zvuka omogućava snimanje zvuka sa zvučne karte i mikrofona istovremeno koristeći WASAPI.
Ovaj dodatak koristi trenutnu zvučnu karticu, ili bluetooth slušalice kao i mikrofon koji je trenutno aktivan, a omogućava snimanje za sada u wave, ili mp3 formatu.

# Instalacija
Jednostavan Snimač Zvuka možete instalirati na 2 načina:

* Koristeći prodavnicu dodataka,
* Preuzimanjem aktuelne verzije dodatka sa stranice  
  [https://github.com/DarkoMilosevic86/EasySoundRecorder/releases](https://github.com/DarkoMilosevic86/EasySoundRecorder/releases)

# Korišćenje
Jednostavan Snimač Zvuka koristite veoma jednostavno koristeći samo 2 komande:

* **Shift+NVDA+R - Pokreće snimanje, pauzira i nastavlja snimanje,
* **Shift+NVDA+T - Zaustavlja snimanje i čuva snimak u `.wav`, ili `.mp3` datoteku, u zavisnosti od podešavanja.

## Važne napomene

* Prilikom gašenja bluetooth slušalica može se dogoditi da Jednostavan Snimač Zvuka ne promeni automatski izlazni uređaj za snimanje, tako da ukoliko snimanje ne započne, morate ponovo pokrenuti NVDA.
* Ukoliko se dogodi da mikrofon blago secka kod snimka, podesite format mikrofona da odgovara formatu vaše zvučne kartice u odeljku Zvuk u kontrolnoj tabli.

Kada instalirate Jednostavan Snimač Zvuka, podrazumevana fascikla u koju se čuvaju snimci je:  
`C:\Users\username\Documents\EasySoundRecorder`

Tako na primer ako je vaše korisničko ime John, snimci će sse po zadatim podešavanjima čuvati u:  
`C:\Users\john\Documents\EasySoundRecorder`

Podrazumevani format snimaka prilikom instalacije Jednostavnog Snimača Zvuka je WAV  
Format snimaka kao i fasciklu u koju se čuvaju snimci možete promeniti u podešavanjima za Jednostavan Snimač Zvuka na sledeći način:  

1. Pritisnite NVDA+N da otvorite NVDA meni,
2. Pritisnite strelicu nadole dok ne čujete Opcije,
3. Pritisnite strelicu udesno
4. Pritiskajte strelicu nadole dok ne čujete Podešavanja Jednostavnog Snimača zvuka...
5. Pritisnite Enter taster, i pojaviće se dijalog za podešavanja Jednostavan Snimača Zvuka.

U ovom dijalogu možete podesiti format čuvanja snimaka:

* WAV
* MP3  

Takođe, možete podesiti i fasciklu u koju će se čuvati snimci.
Možete upisati naziv fascikle, ili aktivirati dugme **Pretraži...** kako biste odabrali fasciklu u koju želite čuvati snimke.

## Važna napomena
Ukoliko fascikla u koju čuvatte snimke ne postoji, ista će biti kreirana pri prvom snimanju.

# Za razvojne programere
Ukoliko želite da doprinesete razvoju Jednostavnog Snimača Zvuka, to možete učiniti na sledeći način:

* Klonirajte Github repozitorijum koristeći sledeću komandu:  
  ```bash
  git clone https://github.com/DarkoMilosevic86/EasySoundRecorder.git
* Izvršite fork ovog repozitorijuma i napravite odgovarajuće promene, bilo da se radi o dodavanju lokalizacije, ili promene u kodu
* Napravite pull request za pridruživanje vaših izmena glavnom repozitorijumu

# Prijavljivanje problema
Ukoliko imate bilo kakvih problema sa radom Jednostavnog Snimača Zvuka, otvorite diskusiju na stranici

[https://github.com/DarkoMilosevic86/EasySoundRecorder/issues](https://github.com/DarkoMilosevic86/EasySoundRecorder/issues)
