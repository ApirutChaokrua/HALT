# An implementation of HALT --- Heart Ake L Tan (2019)
from ply import *
import ply.yacc as yacc
import haltlex

tokens = haltlex.tokens

precedence = (
    ('right', '<-'),
    ('left', '+', '-'),
    ('left', '*', '/'),
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
    stm : stm EOL
         | def_stm
         | var_stm
         | ass_stm
         | if_stm
         | exp_stm
         | loop_stm
         | arr_stm
         | empty
    '''

# Format of all BASIC statements.
# def p_statemen(p):
#     '''statement : INTEGER command NEWLINE'''
    # if isinstance(p[2], str):
    #     print("%s %s %s" % (p[2], "AT LINE", p[1]))
    #     p[0] = None
    #     p.parser.error = 1
    # else:
    #     lineno = int(p[1])
    #     p[0] = (lineno, p[2])

# Blank line
def p_statement_newline(p):
    '''statement : NEWLINE'''
    p[0] = None

# VAR statement
def p_command_let(p):
    '''command : VAR variable EQUALS expr
               | VAR variable '''
    p[0] = ('LET', p[2], p[4])

# PRINT statement
def p_command_print(p):
    '''command : PRINT plist optend'''
    p[0] = ('PRINT', p[2], p[3])

# PRINT statement with no arguments
def p_command_print_empty(p):
    '''command : PRINT'''
    p[0] = ('PRINT', [], None)

# IF-THEN statement
def p_command_if(p):
    '''command : IF relexpr THEN INTEGER'''
    p[0] = ('IF', p[2], int(p[4]))

# FOR statement
def p_loop_stm(p):
    '''
    loop_stm : LOOP  L_BRACKET NUMBER NUMBER R_BRACKET L_CURLYBRACKET stm R_CURLYBRACKET
    '''
# DEFINE statement
def p_def_stm(p):
    '''
    def_stm : DEF ID NUMBER
    '''
# VAR statement
def p_var_stm(p) :
    '''
    var_stm : VAR ID ASSIGN_OP expr
            | VAR ID
    '''

# Expression expressions
def p_expr_binary(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr
            | expr POWER expr'''

    p[0] = ('BINOP', p[2], p[1], p[3])


def p_expr_number(p):
    '''expr : INTEGER
            | FLOAT'''
    p[0] = ('NUM', eval(p[1]))

def p_expr_variable(p):
    '''expr : variable'''
    p[0] = ('VAR', p[1])

def p_expr_group(p):
    '''expr : LPAREN expr RPAREN'''
    p[0] = ('GROUP', p[2])

def p_expr_unary(p):
    '''expr : MINUS expr %prec UMINUS'''
    p[0] = ('UNARY', '-', p[2])
# Assignment statement
def p_ass_stm(p):
    '''
    ass_stm : ID ASSIGN_OP ID
            | ID ASSIGN_OP expr
    ''' 
# IF statement
def p_if_stm(p):
    '''
    if_stm : IF condition QUEST L_CURLYBRACKET stm R_CURLYBRACKET
    '''
# def p_expression_EQ(p):
#     '''expression : expression EQ_OP expression'''
#     p[0] = ('==', p[1], p[3])

# def p_expression_NE(p):
#     'expression : expression NE_OP expression'
#     p[0] = ('!=', p[1], p[3])

def p_condition_LE(p):
    'condition : expr LE_OP expression'
    p[0] = ('<=', p[1], p[3])

def p_condition_GE(p):
    'condition : expression GE_OP expression'
    p[0] = ('>=', p[1], p[3])

def p_condition_less(p):
    '''condition : expression "<" expression'''
    p[0] = ('<', p[1], p[3])


def p_condition_great(p):
    '''condition : expression ">" expression'''
    p[0] = ('>', p[1], p[3])

# Array statement 
def p_arr_stm(p):
    '''
    arr_stm : VAR ID LSBRACKET NUM RSBRACKET
            | VAR ID LSBRACKET NUM RSBRACKET ASSIGN_OP L_CURLYBRACKET list_array R_CURLYBRACKET
    '''
# END statement

# REM statement

# STOP statement
def p_command_stop(p):
    '''command : STOP'''
    p[0] = ('STOP',)

# DEF statement
def p_command_def(p):
    '''command : DEF ID LPAREN ID RPAREN EQUALS expr'''
    p[0] = ('FUNC', p[2], p[4], p[7])


# RETURN statement
def p_command_return(p):
    '''command : RETURN'''
    p[0] = ('RETURN',)

# Relational expressions
def p_relexpr(p):
    '''relexpr : expr LT expr
               | expr LE expr
               | expr GT expr
               | expr GE expr
               | expr EQUALS expr
               | expr NE expr'''
    p[0] = ('RELOP', p[2], p[1], p[3])

# Variables
def p_variable(p):
    '''variable : ID
              | ID LPAREN expr RPAREN
              | ID LPAREN expr COMMA expr RPAREN'''
    if len(p) == 2:
        p[0] = (p[1], None, None)
    elif len(p) == 5:
        p[0] = (p[1], p[3], None)
    else:
        p[0] = (p[1], p[3], p[5])

# Builds a list of variable targets as a Python list
def p_varlist(p):
    '''varlist : varlist COMMA variable
               | variable'''
    if len(p) > 2:
        p[0] = p[1]
        p[0].append(p[3])
    else:
        p[0] = [p[1]]

# Builds a list of numbers as a Python list
def p_numlist(p):
    '''numlist : numlist COMMA number
               | number'''

    if len(p) > 2:
        p[0] = p[1]
        p[0].append(p[3])
    else:
        p[0] = [p[1]]

# A signed number.
def p_number_signed(p):
    '''number  : MINUS INTEGER
               | MINUS FLOAT'''
    p[0] = eval("-" + p[2])

# Empty
def p_empty(p):
    '''empty : '''

# error handler
def p_error(p):
    if not p:
        print("SYNTAX ERROR AT EOF")
    else:
        print("line: '%s'" % p.value)

parser = yacc.yacc()

def parse(data, debug=0):
    parser.error = 0
    p = parser.parse(data, debug=debug)
    if parser.error:
        print("hparser error")
        return None
    return p
