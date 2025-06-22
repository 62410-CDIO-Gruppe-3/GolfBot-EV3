```markdown
# GolfBot-EV3

## 1. Projektbeskrivelse
GolfBot-EV3 er en autonom LEGO Mindstorms EV3-robot, der samler bordtennisbolde op på en bane, identificerer og prioriterer en særlig VIP-bold, og afleverer alle bolde automatisk i en målzone. Robotten kombinerer præcis motorstyring, sensorer og billedgenkendelse for at løse opgaven effektivt og selvstændigt.


### Konkurrenceopsætning
Robotten opererer på en 180x120 cm bane med en midterforhindring (kors) og må ikke røre hverken vægge eller forhindringen.  
Der er 11 bordtennisbolde – herunder én orange VIP-bold, som skal prioriteres.  
Robotten har 8 minutter til at finde, samle og aflevere boldene i en udgangsåbning (mål A/B).


## 2. Hardwarekrav

- LEGO Mindstorms EV3-brick
- 2 x Large Motorer (hjuldrift)
- 2 x Medium Motorer (port/gate og boldskubber)
- Farvesensor
- Touchsensor
- Ultralydssensor
- Gyrosensor
- Samsung S23 Ultra (mobilkamera til billedgenkendelse)
- Diverse LEGO-dele, gear og kabler

---

## 3. Softwarekrav

- EV3 MicroPython (pybricks)
- Python 3 (til PC-baserede moduler, fx vision)
- config.py (centrale konstanter og porte)
- utils.py (hjælpefunktioner)
- main.py (hovedprogram)
- vision.py (billedgenkendelse, kræver fx OpenCV)
- navigation.py (pathfinding og positionsstyring)
- tests/ (testkode til hardware og mekanismer)
- Sørg for, at vision.py kører parallelt med robotkoden, da billedgenkendelse styres eksternt via PC.


---

## 4. Opsætning og installation

### Fysisk opsætning
1. Monter alle motorer og sensorer på EV3-brick i henhold til portdefinitionerne i `config.py`.
2. Placer Samsung S23 Ultra, så kameraet har overblik over banen.
3. Tilslut 12V blæsermotor via ekstern strømforsyning og styringsrelæ.

### Softwareopsætning
1. Installer EV3 MicroPython på EV3-brick ([vejledning her](https://pybricks.com/ev3-micropython/)).
2. Overfør projektfilerne til EV3-brick og PC.
3. Installer nødvendige Python-pakker på PC (fx OpenCV til vision).
4. Tilpas `config.py` hvis porte eller parametre ændres.

### Kørsel
- Start hovedprogrammet på EV3:  
  `python main.py`
- Start vision-modulet på PC:  
  `python vision.py`

---

## 5. Filstruktur

| Fil/Mappe         | Beskrivelse                                                                 |
|-------------------|------------------------------------------------------------------------------|
| `main.py`         | Hovedprogram, styrer robotlogik og sekvenser                                 |
| `config.py`       | Samler alle porte, hastigheder, vinkler og konstanter ét sted                |
| `utils.py`        | Genanvendelige hjælpefunktioner til motorstyring og mekanik                  |
| `hatch.py`        | Funktioner til åbning/lukning af port/gate                                   |
| `hatch2.py`       | Funktioner til boldskubber                                                   |
| `vision.py`       | (Kommende) Billedgenkendelse og VIP-bold identifikation                      |
| `navigation.py`   | (Kommende) Pathfinding og positionsstyring                                   |
| `frame_navigator.py` | Dynamisk styring billede for billede |
| `tests/`          | Testkode til hardware og mekanismer (fx test af motorer og sekvenser)        |

---

## 6. Eksempel på brug

### Kør robotten (på EV3)
```python
from main import main
main()
```
### Naviger billede for billede
```python
from Movement.frame_navigator import FrameNavigator
nav = FrameNavigator([(100, 200), (300, 400)])
nav.run()
```


### Brug hjælpefunktioner direkte
```python
from utils import open_gate, close_gate, push_balls
open_gate(Motor_GATE)
push_balls(Motor_PUSH)
close_gate(Motor_GATE)
```

### Test mekanismer (fra tests/)
```bash
python tests/test_motors.py
```

---

## 7. Kreditering / Forfattere

- Abdulrahman Abdullah
- Mustafa Naama Al-Saadi
- Mardin Eliassi
- Gustav Rotne Hansen
- Gustav Høgh Hansen
- Haleef Abu Talib
- lax

*GolfBot-EV3 er udviklet som en del af CDIO-konkurrencen 2025.*
```
