# dbot

For now you can use this bot to roll dice and receive a graph of the probabilities of outcomes for the die roll.

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

## Prerequisites

* Python 3.7 or greater for @dataclass.

```
pip install discord
pip install python-dotenv
pip install matplotlib
```