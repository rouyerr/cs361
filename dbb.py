from itertools import repeat
import timeit
import import_games
def convert( aString ):
    if aString.lower().startswith("0x"):
        return int(aString,16)
    elif aString.lower().startswith("0b"):
        return int(aString,2)
    else:
        return int(aString)
def display_bitboard(bitboard):
    for rank in range(7, -1, -1):
        print(bin(bitboard >> (rank * 8) & 0xFF)[2:].zfill(8)[::-1])


if __name__ == "__main__":
    #while(1):
    #    try:
    #        display_bitboard (convert(input("bitboard :")))
    #    except Exception as e:
    #        pass

    print(timeit.repeat(import_games.get_lichess_games, number=1, repeat=2))

