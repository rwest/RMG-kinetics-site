#!/usr/bin/env python
# encoding: utf-8
"""
database.py

Created by Richard West on 2009-09-01.
Copyright (c) 2009 MIT. All rights reserved.
"""
import sys
import os
import unittest

def removeCommentFromLine(line):
	"""
	Remove a C++/Java style comment from a line of text.
	"""
	index = line.find('//')
	if index >= 0:
		line = line[0:index]
	return line

class Rate():
    import re
    _Trange_re = re.compile('^[0-9\-.]*$')
    def __init__(self,line=None):
        self.line=line
        if line: 
            self.from_line(line)
    def from_line(self,line):
        tokens = line.split()
        if len(tokens)<12: 
            raise Exception('Not enough tokens in line: %s'%line)
        self.id = tokens.pop(0)
        self.groups=[]
        # while it's not a T-range, it's a group
        while not Rate._Trange_re.match(tokens[0]):
            self.groups.append(tokens.pop(0))
        self.Trange = tokens.pop(0)
    
    
class Family():
    """A reaction family."""
    def __init__(self,path):
        self.path = path
        self.name = os.path.split(path)[1]
        self.rates=[]
        self.rates_dict={}
        self.reaction=''
        self.unread = ''
    def __repr__(self):
        return "Family(%s)"%(self.path)
    def path_to(self,relativepath):
        return os.path.join(self.path,relativepath)
    def load(self):
        self.reaction = file(self.path_to('reactionAdjList.txt')).read()
        for line in file(self.path_to('rateLibrary.txt')):
            shortline = removeCommentFromLine(line).strip()
            if len(shortline.split()) > 11:
                rate = Rate(shortline)
                self.rates.append(rate)
                self.rates_dict[rate.id] = rate
            else:
               self.unread += line
            
    def getRate(self, rate_id):
        return self.rates_dict[rate_id]
        
        
class FamiliesList():
    """A list of reaction families"""
    def __init__(self,path):
        self.list = []
        self.load(path)
        self.__iter__ = self.list.__iter__ # if we iterate on self it behaves as self.list
    def path_to(self,relativepath):
        return os.path.join(self.path,relativepath)
    def load(self,path):
        self.path=path
        for line in file(path):
            line = removeCommentFromLine(line.strip())
            if line:
                (number,onoff,name) = line.split()
                family_path = os.path.join(self.path,name)
                family = Family(family_path) 
                family.number = number
                family.onoff = onoff
                family.name = name
                self.list.append(family)

class Database:
    """The kinetics database"""
    def __init__(self,path='RMG_database/kinetics'):
        self.path=path
        self._familiesList = None
    def path_to(self,relativepath):
        return os.path.join(self.path,relativepath)
        
    def getFamiliesList(self):
        if not self._familiesList:
            self._familiesList = FamiliesList(self.path_to('families.txt'))
        return self._familiesList
        
    def getFamily(self,name):
        """Get a family by name. 
        Returns a Family() instance, or None if it looks like there isn't one"""
        path = self.path_to(name)
        if os.path.exists(path) and os.path.isdir(path):
            return Family(self.path_to(name))
        else: 
            return None
    

class databaseTests(unittest.TestCase):
    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()