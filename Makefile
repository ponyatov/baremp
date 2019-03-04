
all:
	python hello.py && $(MAKE) -C hello

doxy:
	rm -rf docs ; doxygen doxy.gen 1>/dev/null
