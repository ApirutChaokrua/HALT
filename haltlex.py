# An implementation of Dartmouth BASIC (1964)

from ply import *

keywords = (
    'LET', 'READ', 'DATA', 'PRINT', 'GOTO', 'THEN', 'FOR', 'NEXT', 'TO', 'STEP',
    'END', 'GOSUB', 'DIM', 'REM', 'RUN', 'LIST', 'NEW',

    'EXIT', 'DEF', 'VAR', 'IF', 'SHOW', 'SHOWLN', 'LOOP', 'RETURN', 'BREAK', 
    'LE', 'GE', 'EQ','LT', 'GT','MOD', 'LBRACKET', 'RBRACKET', 'LCURLYBRACKET', 'RCURLYCBRACKET', 'LANGLEBRACKET', 'RANGLEBRACKET', 'ASSIGN', 
    'ADD', 'MINUS', 'MUL', 'DIVIDE'
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


t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_GT = r'>'
t_EQ = r'=='
t_MOD = r'mod'
t_LBRACKET = r'\)'
t_RBRACKET = r'\('
t_LCURLYBRACKET = r'\{'
t_RCURLYCBRACKET = r'\}'
t_LANGLEBRACKET = r'\<'
t_RANGLEBRACKET = r'\>'
t_ASSIGN = r'<-'
t_INTEGER = r'\d+'
t_ADD = r'\+'
t_MINUS = r'-'
t_MUL = r'\*'
t_DIVIDE = r'/'

def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1
    return t

def t_error(t):
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)

lex.lex(debug=0)
