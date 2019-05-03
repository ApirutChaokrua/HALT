from ply import *
import ply.lex as lex

keywords = (

    'VAR', 'IF', 'SHOW', 'SHOWLN', 'LOOP', 'HEX', 'hex',
    'LE_OP', 'GE_OP', 'EQ_OP','LT_OP', 'GT_OP','MOD_OP', 
    'L_BRACKET', 'R_BRACKET', 'L_CURLYBRACKET', 'R_CURLYBRACKET', 'L_SBRACKET', 'R_SBRACKET',
    'ASSIGN_OP', 'ADD_OP', 'MINUS_OP', 'MUL_OP', 'DIVIDE_OP',  
    'NUMBER', 'HEX_NUM', 'QUEST','COMMA', 'ID', 'EOL', 'INF','STRING', 'BREAK'
)
tokens = keywords 

t_ignore = ' \t\v\f'
t_COMMA = r'\,'
t_LE_OP = r'<='
t_GE_OP = r'>='
t_LT_OP = r'<'
t_GT_OP = r'>'
t_EQ_OP = r'=='
t_MOD_OP = r'%'
t_R_BRACKET = r'\)'
t_L_BRACKET = r'\('
t_L_CURLYBRACKET = r'\{'
t_R_CURLYBRACKET = r'\}'
t_L_SBRACKET = r'\['
t_R_SBRACKET = r'\]'
t_ASSIGN_OP = r'<-'
t_ADD_OP = r'\+'
t_MINUS_OP = r'-'
t_MUL_OP = r'\*'
t_DIVIDE_OP = r'/'
t_QUEST = r'\?'
t_INF = r'INF'
t_BREAK = r'BREAK'
t_STRING = r'\".*?\"'


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


# ---------------- Comment --------------------
def t_COMMENT(t):
     r'\#.*'
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
