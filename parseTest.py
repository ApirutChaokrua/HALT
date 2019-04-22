# An implementation of HALT --- Heart Ake L Tan (2019)
from ply import *
import ply.yacc as yacc
import haltlex

tokens = haltlex.tokens

precedence = (
    ('right', 'ASSIGN_OP'),
    ('left', 'ADD_OP', 'MINUS_OP'),
    ('left', 'MUL_OP', 'DIVIDE_OP'),
    ('left', 'LE_OP', 'GE_OP','EQ_OP'),
)

# A HALT program is a series of statements.  We represent the program as a
# dictionary of tuples indexed by line number.
def p_code(p):
    '''
    code : code stm
         | stm
    '''
# This catch-all rule is used for any catastrophic errors.  In this case,
# we simply return nothing
def p_code_error(p):
    '''code : error'''
    p[0] = None
    p.parser.error = 1

def p_stm(p):
    '''
    stm : def_stm
         | var_stm
         | assign_stm
         | if_stm
         | exp_stm
         | loop_stm
         | show_stm
         | stop 
         | return
         | empty
         | stm EOL
    '''
    p[0] = p[1]

# Empty
def p_empty(p):
    '''empty : '''

# error handler
def p_error(p):
    if not p:
        print("SYNTAX ERROR AT EOF")
    else:
        print("line: '%s'" % p.value)

hparser = yacc.yacc()

def parse(data, debug=0):
    hparser.error = 0
    p = hparser.parse(data, debug=debug)
    if hparser.error:
        print("hparser error")
        return None
    return p
