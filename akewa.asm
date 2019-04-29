DEFAULT REL
extern printf
extern scanf
extern fflush
global main
section .data
_fmin db "%ld", 0
A dq 5
_LC0 db "KUY", 0
_LC1 db "FUCK", 0
section .text
_input:
push rbp
mov rbp, rsp
sub rsp, 16
lea rax, [rbp - 8]
mov rsi, rax
mov rdi, _fmin
call scanf
mov rax, [rbp - 8]
leave
ret
main:
push rbp
mov rdi, _LC0
mov rdi, _LC1
mov rax, 0
pop rbp
ret
