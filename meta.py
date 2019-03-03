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

## input/output
class IO(Meta): pass

## directory
class Dir(IO):
    def dump(self,depth=0):
        S = IO.dump(self,depth)
        S += self.mk.dump(depth+1)
        S += self.git.dump(depth+1)
        S += self.c.dump(depth+1)
        S += self.h.dump(depth+1)
        return S

## file
class File(IO): pass

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
        self.dir = Dir(self.value)
        self.dir.mk  = File('Makefile')
        self.dir.git = File('.gitignore')
        self.dir.c   = File(self.value+'.c')
        self.dir.h   = File(self.value+'.h')
    def dump(self,depth=0):
        S = Meta.dump(self,depth)
        S += self.dir.dump(depth+1)
        return S
