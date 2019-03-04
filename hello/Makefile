
        
MODULE = $(notdir $(CURDIR))
        
$(MODULE).log: ./$(MODULE).exe
	./$< > $@ && tail $(TAIL) $@
    
C = $(MODULE).c
H = $(MODULE).h

./$(MODULE).exe: $(C) $(H)
	$(CC) -o $@ $(C)
    

