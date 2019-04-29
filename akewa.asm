DEFAULT REL
extern printf
extern scanf
extern fflush
global main
section .data
_fmin db "%ld", 0
A dq 5
_LC0 db A, 0
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
call printf
xor rdi, rdi
call fflush
mov rax, 0
pop rbp
ret
