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

No worries! Just use the bot like this: 

```
Examples:

name add kassler knasboll - adds an untaken name, 'Kassler Knasboll'
name add kASSler kNaSbOlL - ignores case, becomes 'Kassler Knasboll' anyway
name take 32              - takes the name with ID 32
name untake 57            - untakes the name with ID 57
name random               - gives a random untaken name
name randomtake           - takes the name that is randomed, so it won't show up in untaken searches 
name all                  - lists all names
name alltaken             - lists all taken names
name alluntaken           - lists all untaken names

names are displayed to the user with ID:s.
```

## Prerequisites for building

* Python 3.10 or greater.

```
pip install discord
pip install python-dotenv
pip install matplotlib
pip install sqlite3
```