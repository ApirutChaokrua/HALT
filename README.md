# HALT! compiler

It is "HALT!" compiler
Compiler Construction “Elementary Compiler” assignment

## Buid

Buid lexer Parser and run

```
  $ flex test.l
  $ yacc -d test.y
  $ gcc  -o test.exe  test.tab.c 
  
  $ test.exe code.txt

```

Buid via Makefile

```
  $ make 
  $ make clean  

```

### Grammar

assign 

```
A <- 1+2
```


## Authors

* **AAAA AAAAA** - *Initial work* 

## Acknowledgments

* Flex
* Bison
* etc

