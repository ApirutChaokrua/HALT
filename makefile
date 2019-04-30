all:
	# python ak.py
	nasm -f win64 test.asm
	gcc test.obj -o test.exe

clean:
	rm -rf parser.out
	rm -rf parsetab.py
