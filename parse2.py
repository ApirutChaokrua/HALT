# An implementation of HALT --- Heart Ake L Tan (2019)
from ply import *
import ply.yacc as yacc
import haltlex
tokens = haltlex.tokens

precedence = (
    ('right', 'ASSIGN_OP'),
    ('left', 'ADD_OP', 'MINUS_OP'),
    ('left', 'MUL_OP', 'DIVIDE_OP', 'MOD_OP'),
    ('left', 'LE_OP', 'GE_OP', 'EQ_OP','LT_OP', 'GT_OP'),
)

# A HALT program is a series of statements.  We represent the program as a
# dictionary of tuples indexed by line number.
def p_code(p):
    '''
    code : code EOL stm
         | stm
    '''
    if len(p) == 4 :
        p[0] = ('MULTIPLE_LINE',p[1],p[3])
    else:
        p[0] = p[1]

def p_stmSpace(p):
    '''
    stmSpace : stmSpace EOL code
             | EOL code
    '''
    if len(p) == 4 :
        p[0] = p[3]
    else:
        p[0] = p[2]



# This catch-all rule is used for any catastrophic errors.  In this case,
# we simply return nothing
def p_code_error(p):
    '''code : error'''
    p[0] = None
    p.parser.error = 1

def p_stm(p):
    '''
    stm : var_stm
         | assign_stm
         | if_stm
         | exp_stm
         | loop_stm
         | show_stm
         | stop
         | return
         | empty
         | stmSpace
    '''
    p[0] = p[1]
# TYPE OF NUMBER
def p_type_num(p):
    '''
    type_num : ID
             | sign_number
             | list_num
             | NUMBER
             | HEX_NUM
    '''

    if type(p[1]) is str:
        if p[1][:2]=="Hx" or p[1][:2]=="HX":
            p[0] = ('HEX', int(p[1][2:],16))
        else:
            p[0] = p[1]
    else:
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
    else:
        p[0] = ('index', p[1], None)
# DEFINE statement
# def p_def_stm(p):
#     '''
#     def_stm : DEF ID NUMBER
#     '''
#     p[0] = ('DEFINE', p[2], p[3])
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
    var_stm :  VAR ID L_SBRACKET type_num R_SBRACKET ASSIGN_OP L_CURLYBRACKET set_num R_CURLYBRACKET
            |  VAR ID L_SBRACKET type_num R_SBRACKET
    '''
    if(len(p) == 6):
        p[0] = ('VAR_LIST', p[2], str(p[4]), 'none')
    else :
        p[0] = ('VAR_LIST_VALUE', p[2], str(p[4]), p[8])


# Assignment statement
def p_assign_stm(p):
    '''
    assign_stm : ID ASSIGN_OP type_num
               | ID ASSIGN_OP exp_stm
    '''
    p[0] = ('ASSIGN', p[1], p[3])

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
        | L_BRACKET exp_stm R_BRACKET
        | type_num
    '''
    if(len(p) > 2):
        if(p[1] == '('):
            p[0] = ('PAREN',p[1],p[2],p[3])
        else:
            p[0] = ('EXP', p[2], p[1], p[3])
    else:
        p[0] = p[1]

# IF statement
def p_if_stm(p):
    '''
    if_stm : IF condition QUEST L_CURLYBRACKET EOL stm  EOL R_CURLYBRACKET
           | IF condition QUEST L_CURLYBRACKET stm R_CURLYBRACKET

    '''
    if(len(p) == 9):
        p[0] = ('IF', p[2], p[6])
    else :
        p[0] = ('IF', p[2], p[5])

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
    loop_stm : LOOP L_BRACKET type_num R_BRACKET L_CURLYBRACKET  stm  R_CURLYBRACKET
             | LOOP L_BRACKET INF R_BRACKET L_CURLYBRACKET  stm  R_CURLYBRACKET
    '''
    p[0] = ('LOOP', p[3], p[6])
# SHOW statement

def p_showln_var_stm(p):
    '''
    show_stm : SHOWLN L_BRACKET rec_var_msg1 R_BRACKET
    '''
    p[0] = ('SHOWLN', '"%ld"', p[3])


def p_showln_str_stm(p):
    '''
    show_stm : SHOWLN L_BRACKET STRING recursive_str R_BRACKET
    '''
    if(len(p) == 6):
        p[0] = ('SHOWLN', p[3], p[4])

def p_showln_blank_stm(p) :
    '''
    show_stm : SHOWLN L_BRACKET recursive_var R_BRACKET
    '''
    # p[0] = ('SHOWLN', None, None)
    p[0] = ('SHOWLN', None, p[3])

def p_show_var_stm(p):
    '''
    show_stm : SHOW L_BRACKET rec_var_msg1 R_BRACKET
    '''
    p[0] = ('SHOW', '"[%ld]"', p[3])

def p_show_str_stm(p):
    '''
    show_stm : SHOW L_BRACKET STRING recursive_str R_BRACKET
    '''
    if(len(p) == 6):
        p[0] = ('SHOW', p[3], p[4])

def p_show_pass_rec_msg(p):
    '''
    recursive_str : ADD_OP rec_msg
                  | ADD_OP rec_var_msg2
                  | empty
    recursive_var : ADD_OP rec_msg
                  | ADD_OP rec_var_msg2
                  | empty
    '''
    if(len(p) == 2):
        p[0] = p[0] = ("RECURSIVE_MSG", None, None)
    else:
        p[0] = p[2]

def p_show_rec_str_msg(p):
    '''
    rec_msg : STRING recursive_str
    '''
    if(len(p) == 3):
        p[0] = ("SHOW",p[1], p[2])
    else :
        p[0] = ("RECURSIVE_MSG", None, None)

def p_show_rec_var_msg1(p):
    '''
    rec_var_msg1 : type_num recursive_var
    '''
    if(len(p) == 3):
        p[0] = ("RECURSIVE_MSG",p[1], p[2])
    else :
        p[0] = ("RECURSIVE_MSG", None, None)

def p_show_rec_var_msg2(p):
    '''
    rec_var_msg2 : rec_var_msg1
    '''
    if(len(p) == 2):
        p[0] = ("SHOW",'"[%ld]"', p[1])
    else :
        p[0] = ("RECURSIVE_MSG", None, None)

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
    p[0] = eval("-" + str(p[2]))

# Empty
def p_empty(p):
    '''empty : '''

# error handler
def p_error(p):
    print(p)
    if not p:
        print("SYNTAX ERROR AT EOF")
    else:
        print("line: '%s'" % p.value)

hparser = yacc.yacc()
lines = open("test.halt", 'r').read()
tree = hparser.parse(lines)
print(tree)

def getTree():
    return tree


# while True:
#     try:
#         s = input("")
#     except EOFError:
#         break
#     tree = hparser.parse(s)
#     print(tree)

# def parse(data, debug=0):
#     print('EEOEOEOEOEO')
#     hparser.error = 0
#     p = hparser.parse(data, debug=debug)
#     if hparser.error:
#         print("hparser error")
#         return None
#     return p
