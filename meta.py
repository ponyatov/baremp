import os,sys,re

## metaprogramming
class Meta:
    ## construct meta object with given name
    def __init__(self,V):
        ## type/class tag
        self.type  = self.__class__.__name__.lower()
        ## atomic value (implementation language type)
        self.value = V
        ## ordered nested elements
        self.nest  = []
        
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
    def gen(self,parent):
        return self.dump()
    
## container
class Container(Meta): pass

## input/output
class IO(Meta): pass

## plain source code
class Src(IO):
    ## return source as is
    def gen(self,parent):
        return self.value

## source code block
class Block(IO):
    ## create block with optional block comment
    def __init__(self,info='',init=''):
        IO.__init__(self, info)
        for i in init.split('\n'): self.nest.append(i)
    def gen(self,parent):
        S = ''
        if self.value: S += parent.comment(self.value) 
        S += reduce(lambda a,b: a+b.gen(), self.nest)
        return S

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
    def gen(self,parent):
        try: os.mkdir(self.value)
        except OSError: pass
        
        self.git.gen(self)
        self.mk.gen(self)
        self.c.gen(self)
        self.h.gen(self)

## file
class File(IO):
    ## construct file with given name (w/o path)
    def __init__(self,name,init=''):
        assert re.match(r'^(\.gitignore|Makefile|[a-z]+\.[ch])$',name)
        IO.__init__(self, name)
        ## nested elements will we written into output file (ordered)
        if isinstance(init,str):
            for i in init.split('\n'):
                self.nest.append(Src(i))
        if isinstance(init, list):
            self.nest = init
    ## produce file
    def gen(self,parent):
        with open(parent.value+'/'+self.value,'w') as F:
            for i in self.nest:
                print >>F,i.gen(self)
    ## dump contents
    def dump(self,depth=0):
        S = IO.dump(self, depth)
        for j in self.nest:
            S += self.pad(depth+1) + j
        return S
                
## Makefile
class Makefile(File):
    def comment(self,text):
        return '# %s\n'%text
    def __init__(self,name='Makefile'):
        File.__init__(self, name, [
            Block('detect module name from current dir',
                  init='MODULE = $(notdir $(CURDIR))'),
            Block('default target is logged batch',
                  init='$(MODULE).log: ./$(MODULE).exe\n\t./$< > $@ && tail $(TAIL) $@'),
            Src('''
    
C = $(MODULE).c
H = $(MODULE).h

./$(MODULE).exe: $(C) $(H)
\t$(CC) -o $@ $(C)
    
''')])

## .c file
class CFile(File):
    def __init__(self,name):
        self.module = name
        File.__init__(self, name+'.c', \
            '#include "%s.h"\nint main(){}' % self.module )

## .h file
class HFile(File):
    def __init__(self,name):
        self.module = name
        File.__init__(self, name+'.h', \
            '#ifndef %(s)s\n#define %(s)s\n#endif // %(s)s' % \
                {'s':'_H_'+self.module.upper()})

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
        self.dir.mk  = Makefile()
        self.dir.git = File('.gitignore','*~\n*.swp\n*.o\n*.exe\n*.log')
        self.dir.c   = CFile(self.value)
        self.dir.h   = HFile(self.value)
    ## dump generic project structure
    def dump(self,depth=0):
        S = Meta.dump(self,depth)
        S += self.dir.dump(depth+1)
        return S
    ## generate project elements
    def gen(self,parent):
        self.dir.gen(self)
