# Kohlekraft, nein danke!
## Spill for skoleoppgave

## How 2 play

1. Git clone eller last ned repo som zip fil og pakk ut
2. Last ned pygame: `pip install pygame-ce`
3. Kjør `main.py`

### Arguments
Man kan kjøre spillet med spesielle arguments som:

```
--editor, -e: kjør level editor
--hitbox: vis hitboxen til spilleren
--skip-intro, -i: skip introen
```

## Resette spill

For å resette levlene man har gjort ferdig (eller jukse med hvilke du har gjort) så sett `completed_levels = []` i `completed_levels.py`

## Videreutvikle
Det er lett å lage nye levler og nye bygge blokker

Bruk level editor for å lage nye levler (husk og klikk save)

For å legge til nye tiles er det så lett som å lage et 32x32 bilde, og legge det i `assets/images/tiles` med et tall som følger rekkefølgen

## Bugs / forbedringspotensiale

- Ustabil / buggy fysikk
- Ting starter på 0 og ikke 1
- Navn på levler
- Toast notifications til ting som lagring etc..
- Ryddigere kode