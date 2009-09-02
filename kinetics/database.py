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
    __re_Trange = re.compile('^[0-9\-.]*$')
    def __init__(self,line=None):
        self.line=line
        if line: 
            self.from_line(line)
    def from_line(self,line):
        tokens = line.split()
        if len(tokens)<12: 
            raise Exception('Not enough tokens in line: %s'%line)
        self.id = tokens.pop(0).rstrip('.')
        self.groups=[]
        # while it's not a T-range, it's a group
        while not self.__re_Trange.match(tokens[0]):
            self.groups.append(tokens.pop(0))
        self.Trange = tokens.pop(0)
        (  self.A,  self.n,  self.alpha,  self.E0, 
           self.DA, self.Dn, self.Dalpha, self.DE0,
           self.rank) = tokens[:9] # first 9 tokens
        self.comment = ' '.join(tokens[9:]) # the rest
         

class Comment():
    def __init__(self):
        self.id=None

class CommentList():
    import re
    __re_underline = re.compile('^\-+')
    def __init__(self,path):
        """Lazy - does not load data until needed"""
        self.path = path
        self.comments_dict = dict()
    def load(self):
        comment_id = 'General' #mops up comments before the first rate ID
        self.comments_dict[comment_id] = ''
        comment_file = file(self.path)
        for line in comment_file:
            match = self.__re_underline.match(line)
            if match:
                comment_id = comment_file.next().strip()
                assert line.rstrip()==comment_file.next().rstrip(), "Overline didn't match underline"
                if not self.comments_dict.has_key(comment_id):
                    self.comments_dict[comment_id] = ''
                line = comment_file.next()
            self.comments_dict[comment_id] += line
    def get_comment_by_id(self, comment_id):
        """Get a comment by its id (like a dictionary). 
         Loads the data first if required. Returns '' if no comment."""
        if not self.comments_dict:
            self.load()
        try:
            return self.comments_dict[comment_id]
        except KeyError:
            return ''
            #return "no comment for rxn '%s'"%comment_id
    __getitem__ = get_comment_by_id
    
class Family():
    """A reaction family."""
    def __init__(self,path):
        self.path = path
        self.name = os.path.split(path)[1]
        self.rates=[]
        self.rates_dict={}
        self.reaction=''
        self.reverse=''
        self.unread = ''
        self.actions = ''
        self._comment_list = None
    def __repr__(self):
        return "Family(%s)"%(self.path)
    def path_to(self,relativepath):
        return os.path.join(self.path,relativepath)
    def load(self):
        import re
        for line in file(self.path_to('reactionAdjList.txt')):
            shortline = removeCommentFromLine(line).strip()
            if not shortline:
                continue
            if not self.reaction: # first nonblank line is the reaction def'n.
                self.reaction = shortline 
                continue
            rev = re.match('reverse.*?:\s+(\S+)',shortline)
            if rev:
                self.reverse = rev.group(1)
            if not re.match('^\(\d+\)\s+',shortline):
                continue # not an action
            self.actions+=shortline+'\n'
        
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
        
    def getCommentList(self):
        if not self._comment_list:
            self._comment_list = CommentList(self.path_to('comments.rst'))
        return self._comment_list
        
        
class FamiliesList():
    """A list of reaction families"""
    def __init__(self,path):
        self.list = []
        self.load(path)
        self.__iter__ = self.list.__iter__ # if we iterate on self it behaves as self.list
    def path_to(self,relativepath):
        folderpath = os.path.dirname(self.path)
        return os.path.join(folderpath,relativepath)
    def load(self,path):
        self.path=path
        for line in file(path):
            line = removeCommentFromLine(line.strip())
            if line:
                (number,onoff,name) = line.split()
                family_path = self.path_to(name)
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
    
    def convert_comments_to_rST(self):
        """Convert comments files to reStructuredText"""
        import re
        __re_commentID = re.compile('^(\d+):\s+(.*)')
        for family in self.getFamiliesList():
            if not os.path.exists(family.path_to('comments.txt')): 
                continue
            in_file = file(family.path_to('comments.txt'))
            out_file = file(family.path_to('comments.rst'),'w')
            for line in in_file:
                match = __re_commentID.match(line)
                if match:
                    comment_id = match.group(1)
                    line = match.group(2)
                    underline = '-'*len(comment_id)+'\n'
                    out_file.writelines(['\n',underline,comment_id+'\n',underline])
                if line and line[0]=='\t': # remove the first tab
                    line = line[1:]
                if line and line[0]==' ': # remove the first space
                    line = line[1:]
                if line and re.match('^\s+',line): # if still whitespace, keep together
                    line = line.lstrip()
                else:  # otherwise insert a blank line (paragraph break)
                    line = line+'\n'
                      
                out_file.write(line)
            in_file.close()
            out_file.close()


class databaseTests(unittest.TestCase):
    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()