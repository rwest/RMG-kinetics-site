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
import re
from django.conf import settings
# fire up the big guns
sys.path.append(settings.RMG_PATH)
import rmg
import rmg.data


def loadKineticsDatabases(databasePath, only_families=False):
    """
    Create and load the kinetics databases (reaction families).
    If only_families is a list like ['H_Abstraction'] then only families in this
    list will be loaded.
    
    Currently incompatible with RMG(java) database syntax.
    """
    rmg.reaction.kineticsDatabase = rmg.reaction.ReactionFamilySet()
    rmg.reaction.kineticsDatabase.load(databasePath, only_families=only_families)
    
    
def removeCommentFromLine(line):
    """
    Remove a C++/Java style comment from a line of text.
    """
    index = line.find('//')
    if index >= 0:
        line = line[0:index]
    return line
    
class Uncertainty():
    def __init__(self,token='0'):
        self.from_string(token)
    def __repr__(self):
        return "Uncertainty(%s)"%self.string
    def __str__(self):
        """Used by Django, so return HTML"""
        convert={True:'&times;/&divide;', False:'&plusmn;'}
        return "%s %g"%(convert[self.timesdivide],self.value)
#    def __unicode__(self):
#        convert={True:u'÷', False:u'±'}
#        return " %s %g"%(convert[self.timesdivide],self.value)
    def toPython(self):
        """Used in python output. Returns tuple eg. ('+-', 4.0) """
        convert={True:'*/', False:'+-'}
        return convert[self.timesdivide], self.value
    
    def from_string(self,token):
        self.string = token
        token=token.strip()
        if token[0]=='*':
            self.timesdivide = True
            token = token[1:]
        else:
            self.timesdivide = False
        self.value=float(token)

class Rate():
    
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
        if re.search('-',self.Trange):
            self.Tmin, self.Tmax = self.Trange.split('-')
        else:
            self.Tmin = self.Trange
            self.Tmax = None
        (  self.A,  self.n,  self.alpha,  self.E0, 
           self.DA, self.Dn, self.Dalpha, self.DE0,
           self.rank) = tokens[:9] # first 9 tokens
        self.DA = Uncertainty(self.DA)
        self.Dn = Uncertainty(self.Dn)
        self.Dalpha = Uncertainty(self.Dalpha)
        self.DE0 = Uncertainty(self.DE0)
        self.rank = int(self.rank)
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
        self.load()
    def load(self):
        comment_id = 'General' #mops up comments before the first rate ID
        self.comments_dict[comment_id] = ''
        if not os.path.exists(self.path):
            self.comments_dict[comment_id] = "No comments file"
            return 
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
    def __init__(self, path, load_now=True):
        self.path = path
        self.name = os.path.split(path)[1]
        if load_now: self.load() 
    def __repr__(self):
        return "Family(%s)"%(self.path)
    def path_to(self,relativepath):
        return os.path.join(self.path,relativepath)
    def load(self):
        """Load all the stuff"""
        self.load_template()
        self.load_library()
        self.load_dictionary()
        self.load_tree()
        self.load_comment_list()
    def load_template(self):
        import re
        self.reaction=''
        self.reverse=''
        self.actions = ''
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
    def load_library(self):
        self.rates=[]
        self.unread=''
        self.rates_dict={}
        for line in file(self.path_to('rateLibrary.txt')):
            shortline = removeCommentFromLine(line).strip()
            if len(shortline.split()) > 11:
                rate = Rate(shortline)
                self.rates.append(rate)
                self.rates_dict[rate.id] = rate
            else:
                self.unread += line   
    def load_dictionary(self):
        import rmg
        dd=rmg.data.Dictionary()
        dd.load(self.path_to('dictionary.txt'))
        self.dictionary = dd 
    def load_tree(self):
        import rmg
        tt = rmg.data.Tree()
        tt.load(self.path_to('tree.txt'))
        self.tree = tt
    def load_comment_list(self):
        self.comment_list = CommentList(self.path_to('comments.rst'))
        
    def get_rate(self, rate_id):
        return self.rates_dict[rate_id]
    def get_comment(self, rate_id):
        return self.comment_list[rate_id]
    def get_group(self, group_id):
        return self.dictionary[group_id]
        
class FamiliesList():
    """A list of reaction families"""
    def __init__(self,path):
        self.path = path
        self.load()
        self.__iter__ = self.list.__iter__ # if we iterate on self it behaves as self.list
    def path_to(self,relativepath):
        folderpath = os.path.dirname(self.path)
        return os.path.join(folderpath,relativepath)
    def load(self):
        self.list = []
        self.dict = {}
        for line in file(self.path):
            line = removeCommentFromLine(line.strip())
            if line:
                (number,onoff,name) = line.split()
                family_path = self.path_to(name)
                family = Family(family_path)
                family.number = number
                family.onoff = onoff
                family.name = name
                self.list.append(family)
                self.dict[family.name] = family
                
    def get_family(self,name):
        return self.dict[name]

class Database:
    """The kinetics database"""
    def __init__(self,path='RMG_database/kinetics_groups'):
        self.path=path
        self.load()
        
    def path_to(self,relativepath):
        return os.path.join(self.path,relativepath)
        
    def load(self):
        self.families_list = FamiliesList(self.path_to('families.txt'))

    def get_family(self,name):
        """Get a family by name."""
        return self.families_list.get_family(name)


    
    def convert_comments_to_rST(self):
        """Convert comments files to reStructuredText files. Run it once!"""
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