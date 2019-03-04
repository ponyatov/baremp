import os,sys,re

## metaprogramming
class Meta:
    ## construct meta object with given name
    def __init__(self,V):
        ## type/class tag
        self.type  = self.__class__.__name__.lower()
        ## atomic value (implementation language type)
        self.value = V
        
    ## @name dump objects
    
    ## dump object
    def __repr__(self):
        return self.dump()
    ## dump object in tree format
    def dump(self,depth=0):
        S = self.pad(depth) + self.head()
        return S
    ## short dump: header only
    def head(self):
        return '<%s:%s>' %(self.type,self.value)
    ## tabulate dump
    def pad(self,N):
        return '\n'+'    '*N
    
    ## generate source code
    def gen(self):
        pass

## input/output
class IO(Meta): pass

## directory
class Dir(IO):
    ## dump directory members
    def dump(self,depth=0):
        S = IO.dump(self,depth)
        S += self.mk.dump(depth+1)
        S += self.git.dump(depth+1)
        S += self.c.dump(depth+1)
        S += self.h.dump(depth+1)
        return S
    ## generate subelements
    def gen(self):
        try: os.mkdir(self.value)
        except OSError: pass
        
        self.mk.nest = '''
        
MODULE = $(notdir $(CURDIR))
        
$(MODULE).log: ./$(MODULE).exe
\t./$< > $@ && tail $(TAIL) $@
    
C = $(MODULE).c
H = $(MODULE).h

./$(MODULE).exe: $(C) $(H)
\t$(CC) -o $@ $(C)
    
'''.split('\n')
        self.mk.gen(self.value)
        
        self.git.nest += ['*~','*.swp','','*.o','*.exe','*.log','']
        self.git.gen(self.value)
        
        self.c.nest = ( '''

#include "%(module)s.h"

int main(){}
        
''' % {'module':self.value} ).split('\n')
        self.c.gen(self.value)
        
        self.h.nest = ( '''
        
#ifndef _H_%(module)s
#define _H_%(module)s

#endif // _H_%(module)s

''' % {'module':self.value.upper()} ).split('\n')
        self.h.gen(self.value)

## file
class File(IO):
    ## construct file with given name (w/o path)
    def __init__(self,name):
        assert re.match(r'^(\.gitignore|Makefile|[a-z]+\.[ch])$',name)
        IO.__init__(self, name)
        ## nested elements will we written into output file (ordered)
        self.nest = []
    ## produce file
    def gen(self,path):
        with open(path+'/'+self.value,'w') as F:
            for i in self.nest:
                print >>F,i

## programming language
class Lang(Meta): pass

## embedded C language elements
class emC(Lang): pass

## sw/project
class Project(Meta):
    ## define project with given name
    def __init__(self,name):
        assert re.match(r'^[a-zA-Z_][a-zA-Z_0-9]*$',name)
        Meta.__init__(self, name)
        ## project directory
        self.dir = Dir(self.value)
        self.dir.mk  = File('Makefile')
        self.dir.git = File('.gitignore')
        self.dir.c   = File(self.value+'.c')
        self.dir.h   = File(self.value+'.h')
    ## dump generic project structure
    def dump(self,depth=0):
        S = Meta.dump(self,depth)
        S += self.dir.dump(depth+1)
        return S
    ## generate project elements
    def gen(self):
        self.dir.gen()
