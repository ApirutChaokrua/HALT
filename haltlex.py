# An implementation of Dartmouth BASIC (1964)

from ply import *

keywords = (
    'LET', 'READ', 'DATA', 'PRINT', 'GOTO', 'THEN', 'FOR', 'NEXT', 'TO', 'STEP',
    'END', 'GOSUB', 'DIM', 'REM', 'RUN', 'LIST', 'NEW',

    'EXIT', 'DEF', 'VAR', 'IF', 'SHOW', 'SHOWLN', 'LOOP', 'RETURN', 'BREAK', 
    'LE_OP', 'GE_OP', 'EQ_OP','LT_OP', 'GT_OP','MOD_OP', 'L_BRACKET', 'R_BRACKET', 'L_CURLYBRACKET', 'R_CURLYCBRACKET', 'L_ANGLEBRACKET', 'R_ANGLEBRACKET', 'ASSIGN_OP', 
    'ADD_OP', 'MINUS_OP', 'MUL_OP', 'DIVIDE_OP', 'SIGN_INTEGER'
)
tokens = keywords + (
    'EQUALS', 'TIMES', 'POWER',
    'LPAREN', 'RPAREN', 'NE',
    'COMMA', 'SEMI', 'INTEGER', 'FLOAT', 'STRING',
    'ID', 'NEWLINE'
)

t_ignore = ' \t'

def t_REM(t):
    r'REM .*'
    return t

def t_IDENTIFIER(t):
    r'[A-Z][A-Z0-9]*'
    if t.value in keywords:
        t.type = t.value
    return t

def t_ID(t):
    r'[A-Z][A-Z0-9]*'
    if t.value in keywords:
        t.type = t.value
    return t

# t_PLUS = r'\+'
# t_MINUS = r'-'
# t_DIVIDE = r'/'
# t_LT = r'<'
# t_LE = r'<='
# t_GT = r'>'
# t_GE = r'>='
# t_INTEGER = r'\d+'

t_EQUALS = r'='
t_TIMES = r'\*'
t_POWER = r'\^'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_NE = r'<>'
t_COMMA = r'\,'
t_SEMI = r';'
t_FLOAT = r'((\d*\.\d+)(E[\+-]?\d+)?|([1-9]\d*E[\+-]?\d+))'
t_STRING = r'\".*?\"'



t_LE_OP = r'<='
t_GE_OP = r'>='
t_LT_OP = r'<'
t_GT_OP = r'>'
t_EQ_OP = r'=='
t_MOD_OP = r'mod'
t_L_BRACKET = r'\)'
t_R_BRACKET = r'\('
t_L_CURLYBRACKET = r'\{'
t_R_CURLYCBRACKET = r'\}'
t_L_ANGLEBRACKET = r'\<'
t_R_ANGLEBRACKET = r'\>'
t_ASSIGN_OP = r'<-'
t_INTEGER = r'\d+'
t_SIGN_INTEGER = r'[+-]?[0-9]+'
t_HEX_INTEGER = r'(Hx)?[a-fA-F0-9]+'
t_ADD_OP = r'\+'
t_MINUS_OP = r'-'
t_MUL_OP = r'\*'
t_DIVIDE_OP = r'/'

def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1
    return t

def t_error(t):
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex(debug=0)

# test Laxer
lexer.input("1+2")

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)

