# GolfBot EV3

## 🤖 Formål
GolfBot er en autonom robot bygget med LEGO EV3, som indsamler bordtennisbolde på en konkurrencebane uden at røre vægge eller forhindringer. Den bruger billedgenkendelse fra en Samsung S23 Ultra, som sender billeder til en computer, hvorfra den styres.

## 🛠️ Hardware
- LEGO EV3 (2 Large motors, 2 Medium motors)
- Farvesensor, Ultrasonisk sensor, Infrarød sensor, Gyrosensor
- 12V-blæser (ekstern)
- Bold-port og bagudgående skubberarm

## 🧠 Software
- EV3 MicroPython (pybricks)
- Computer til billedanalyse og styring
- Bluetooth/Wi-Fi (kommende integration)

## 📂 Projektstruktur
- `main.py`: Hovedprogram
- `utils.py`: Hjælpefunktioner til motorer
- `config.py`: Konfigurationsparametre
- `tests/`: Simple testfiler
- `README.md`: Denne fil
