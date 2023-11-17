"""
Module: cache_block.py
Author: Manikanta Varaganti
Date: November 10, 2023
Description: This module contains the Class Cache Block which represents a line in Cache.
"""


class CacheBlock:
    def __init__(self):
        # block attributes
        self.isDirty = False
        self.tag = None
        self.way = None
        self.validity = False
        self.address = None

    def _setAddress(self, address):
        self.address = address

    def _getAddress(self):
        return self.address

    def _setTag(self, tag):
        self.tag = tag

    def _getTag(self):
        return self.tag

    def _getWay(self):
        return self.way

    def _setDirty(self):
        self.isDirty = True

    def _resetDirty(self):
        self.isDirty = False

    def _setWay(self, way):
        self.way = way

    def _getValidity(self):
        return self.validity

    def _setValidity(self):
        self.validity = True

    def _resetValidity(self):
        self.validity = False

    def _resetAll(self):
        self.isDirty = False
        self.tag = None
        self.way = None
        self.validity = False
        self.address = None
