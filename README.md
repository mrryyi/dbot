# dbot

A discord bot that helps with some aspects of dungeon mastering, such as dice rolls or names.

## Dice

You can roll dice and receive a graph of the probabilities of outcomes for the die roll.

```
Examples:
dice 4d12
dice 2d6
dice 1d13
dice 5d6
dice g 4d4     - Show graph of result probability distribution
dice gnor 2d12 - No result, only graph
```

![There should be an image of a graph here.](https://github.com/mrryyi/dbot/blob/main/docimages/example.png "Title")

Graph is generated in-memory and does not need to be stored to save our precious hardware and time.

## Names

Did your players just wonder what your barmaid is called? Or what asked what name their summoned rat has?

No worries! Just type use this bot to 

```
Examples:

name add kassler knasboll - adds an untaken name, 'Kassler Knasboll'
name add kASSler kNaSbOlL - ignores case, becomes 'Kassler Knasboll' anyway
name all                  - lists all names
name alltaken             - lists all taken names
name alluntaken           - lists all untaken names
name random               - gives a random untaken name
name randomtake           - takes the name that is randomed, so it won't show up in untaken searches 
```

## Prerequisites for building

* Python 3.7 or greater for @dataclass.

```
pip install discord
pip install python-dotenv
pip install matplotlib
pip install sqlite3
```