# An implementation of Dartmouth BASIC (1964)

from ply import *
import ply.lex as lex

keywords = (
    # 'LET', 'READ', 'DATA', 'PRINT', 'GOTO', 'THEN', 'FOR', 'NEXT', 'TO', 'STEP',
    # 'END', 'GOSUB', 'DIM', 'REM', 'RUN', 'LIST', 'NEW',

    'DEF', 'VAR', 'IF', 'SHOW', 'SHOWLN', 'LOOP', 
    'LE_OP', 'GE_OP', 'EQ_OP','LT_OP', 'GT_OP','MOD_OP', 'L_BRACKET', 'R_BRACKET', 'L_CURLYBRACKET', 
    'R_CURLYBRACKET',  'ASSIGN_OP', 
    'ADD_OP', 'MINUS_OP', 'MUL_OP', 'DIVIDE_OP',  'NUMBER', 
    'HEX_NUM','L_SBRACKET', 'R_SBRACKET', 'QUEST','COMMA', 'ID','EXIT','RETURN', 'EOL', 'INF','STRING'
    # , 'HEX_NUMBER',, 'NEWLINE', 'SIGN_NUMBER' ,  'L_ANGLEBRACKET', 'R_ANGLEBRACKET', 'SEMI'  ,

)
tokens = keywords 

t_ignore = ' \t\v\f'

def t_REM(t):
    r'REM .*'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_HEX_NUM(t):
    r'[H][xX][0-9a-fA-F]+'
    return t

def t_ID(t):
    r'[_a-zA-Z][_a-zA-Z0-9]*'
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

# t_EQUALS = r'='
# t_TIMES = r'\*'
# t_POWER = r'\^'
# t_LPAREN = r'\('
# t_RPAREN = r'\)'
# t_NE = r'<>'
t_COMMA = r'\,'
# t_SEMI = r';'
# t_FLOAT = r'((\d*\.\d+)(E[\+-]?\d+)?|([1-9]\d*E[\+-]?\d+))'

t_LE_OP = r'<='
t_GE_OP = r'>='
t_LT_OP = r'<'
t_GT_OP = r'>'
t_EQ_OP = r'=='
t_MOD_OP = r'mod'
t_R_BRACKET = r'\)'
t_L_BRACKET = r'\('
t_L_CURLYBRACKET = r'\{'
t_R_CURLYBRACKET = r'\}'
# t_L_ANGLEBRACKET = r'\<'
# t_R_ANGLEBRACKET = r'\>'
t_L_SBRACKET = r'\['
t_R_SBRACKET = r'\]'
t_ASSIGN_OP = r'<-'
# t_NUMBER = r'\d+'
# t_SIGN_NUMBER = r'[-]?[0-9]+'
# t_HEX_NUMBER = r'(Hx)?[a-fA-F0-9]+'
t_ADD_OP = r'\+'
t_MINUS_OP = r'-'
t_MUL_OP = r'\*'
t_DIVIDE_OP = r'/'
t_QUEST = r'\?'
t_INF = r'INF'
t_STRING = r'\".*?\"'

# ---------------- Comment --------------------
def t_COMMENT(t):
     r'\#.*'
     pass

     # No return value. Token discarded
def t_ccode_comment(t):
    r'(/\*(.|\n)*?\*/)|(//.*)'
    pass
# ----------------------------------------------

def t_EOL(t):
    r'\n'
    t.lexer.lineno += 1
    t.type = "EOL"
    return t

def t_error(t):
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex(debug=0)

# test Laxer
lexer.input("")


while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
