all: 
	flex test.l
	bison -d test.y
	gcc -o test.exe test.tab.c

clean:
	rm -rf lex.yy.c
	rm -rf test.tab.c
	rm -rf test.tab.h
	rm -rf test.exe