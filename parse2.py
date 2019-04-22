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
# TYPE OF NUMBER
def p_type_num(p):
    '''
    type_num : ID
             | sign_number
             | list_num
             | NUMBER
    '''
    p[0] = p[1]

def p_list_num(p):
    '''
    list_num : ID L_SBRACKET type_num R_SBRACKET
    '''  
    p[0] = ('LIST', p[1], p[3])
def p_set_num(p):
    '''
    set_num : NUMBER COMMA set_num
            | NUMBER
    '''   
    if(len(p) > 2):
        p[0] = ('index', p[1], p[3])
# DEFINE statement
def p_def_stm(p):
    '''
    def_stm : DEF ID NUMBER
    '''
    p[0] = ('DEFINE', p[2], p[3])
# VAR statement
def p_var_stm(p):
    '''
    var_stm : VAR ID ASSIGN_OP type_num
            | VAR ID ASSIGN_OP exp_stm
            | VAR ID 
    '''
    if(len(p) == 3):
        p[0] = ('VAR', p[2], '0')
    else :
        p[0] = ('VAR', p[2], p[4])

def p_var_stm_list(p):
    ''' 
    var_stm : VAR ID L_SBRACKET NUMBER R_SBRACKET
            | VAR ID L_SBRACKET type_num R_SBRACKET ASSIGN_OP L_CURLYBRACKET set_num R_CURLYBRACKET
    '''
    if(len(p) == 6):
        p[0] = ('VAR_LIST', p[2], p[4], 'none')
    else :
        p[0] = ('VAR_LIST_VALUE', p[2], p[4], p[7])


# Assignment statement
def p_assign_stm(p):
    '''
    assign_stm : ID ASSIGN_OP type_num
               | ID ASSIGN_OP exp_stm
    ''' 

def p_exp_stm(p):
    # '''
    # exp_stm : exp_stm ADD_OP term
    #         | exp_stm MINUS_OP term
    # term : term MUL_OP factor
    #      | term DIVIDE_OP factor
    #      | factor
    # factor : type_num
    # '''
    
    '''exp_stm : exp_stm ADD_OP exp_stm
        | exp_stm MINUS_OP exp_stm
        | exp_stm MUL_OP exp_stm
        | exp_stm DIVIDE_OP exp_stm
        | exp_stm MOD_OP exp_stm
        | type_num
    '''
    if(len(p) > 2):
        p[0] = ('EXP', p[2], p[1], p[3])

# IF statement
def p_if_stm(p):
    '''
    if_stm : IF condition QUEST L_CURLYBRACKET stm R_CURLYBRACKET
    '''
def p_condition_LE(p):
    'condition : exp_stm LE_OP exp_stm'
    p[0] = ('LE_OP', p[1], p[3])

def p_condition_GE(p):
    'condition : exp_stm GE_OP exp_stm'
    p[0] = ('GE_OP', p[1], p[3])

def p_condition_less(p):
    '''condition : exp_stm LT_OP exp_stm'''
    p[0] = ('LT_OP', p[1], p[3])

def p_condition_great(p):
    '''condition : exp_stm GT_OP exp_stm'''
    p[0] = ('GT_OP', p[1], p[3])    

def p_condition_EQ(p):
    '''condition : exp_stm EQ_OP exp_stm'''
    p[0] = ('EQ_OP', p[1], p[3])

# LOOP statement
def p_loop_stm(p):
    '''
    loop_stm : LOOP L_BRACKET type_num R_BRACKET L_CURLYBRACKET stm R_CURLYBRACKET
             | LOOP L_BRACKET INF R_BRACKET L_CURLYBRACKET stm R_CURLYBRACKET
    '''
# SHOW statement
def p_show_stm(p):
    '''
    show_stm : SHOW msg
             | SHOWLN
    msg : msg ADD_OP msg
        | type_num
        | STRING
        | empty
    '''

# EXIT statement
def p_stop(p):
    '''stop : EXIT'''
    p[0] = ('EXIT',)

# RETURN statement
def p_return(p):
    '''return : RETURN'''
    p[0] = ('RETURN',)

# A signed number.
def p_number_signed(p):
    '''sign_number  : MINUS_OP NUMBER
    '''
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

hparser = yacc.yacc()

def parse(data, debug=0):
    hparser.error = 0
    p = hparser.parse(data, debug=debug)
    if hparser.error:
        print("hparser error")
        return None
    return p
