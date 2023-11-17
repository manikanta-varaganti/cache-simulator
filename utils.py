"""
Module: utils.py
Author: Manikanta Varaganti
Date: November 10, 2023
Description: This module contains the utility functions that are used for address conversion.
"""


# formats the addresses properly
def fixAddress(str):
    return str.strip().lower().zfill(8)


# converts the hexadecimal address to binary address
def hexToBin(addr):
    hex_dict = {
        "0": "0000",
        "1": "0001",
        "2": "0010",
        "3": "0011",
        "4": "0100",
        "5": "0101",
        "6": "0110",
        "7": "0111",
        "8": "1000",
        "9": "1001",
        "a": "1010",
        "b": "1011",
        "c": "1100",
        "d": "1101",
        "e": "1110",
        "f": "1111",
    }
    binary = ""
    for digit in addr:
        binary += hex_dict[digit]
    return binary


# converts binary address to hexadecmial address
def binToHex(addr):
    return format(int(addr, 2), "x")


# converts a binary string to decimal
def binToDec(addr):
    return int(addr, 2)
