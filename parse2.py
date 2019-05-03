# An implementation of HALT --- Heart Ake L Tan (2019)
from ply import *
import ply.yacc as yacc
import haltlex
tokens = haltlex.tokens
import sys
isError = True


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
    code_loop : code_loop EOL inside_loop_stm
              | inside_loop_stm
    '''
    if len(p) == 4 :
        p[0] = ('MULTIPLE_LINE',p[1],p[3])
    else:
        p[0] = p[1]


def p_stmSpace(p):
    '''
    stmSpace : stmSpace EOL code
             | EOL code
    stmSpace_loop : stmSpace_loop EOL code_loop
                  | EOL code_loop
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
         | assign_list_stm
         | if_stm
         | loop_stm
         | show_stm
         | empty
         | stmSpace

    inside_loop_stm : if_stm_loop
                    | break_stm
                    | var_stm
                    | assign_stm
                    | assign_list_stm
                    | loop_stm
                    | show_stm
                    | empty
                    | stmSpace_loop

    '''
    p[0] = p[1]

# def p_stm_error(p):
#     '''
#     stm : exp_stm
#     inside_loop_stm : exp_stm
#     '''
#     errline = p.lineno(1)
#     print("Syntax error in statement. Bad expression at line: %s '%s'" % (errline, p[1]))


# TYPE OF NUMBER
def p_type_num(p):
    '''
    type_num : sign_number
             | NUMBER
             | HEX_NUM
             | list_num
             | MINUS_OP ID
             | MINUS_OP list_num
             | ID
    type_var_num : list_num
                 | MINUS_OP ID
                 | MINUS_OP list_num
                 | ID
    type_hex_num : NUMBER
                 | HEX_NUM
                 | list_num
                 | MINUS_OP ID
                 | MINUS_OP list_num
                 | ID
    type_list_num : ID
                  | NUMBER
    type_if_num : sign_number
             | NUMBER
             | HEX_NUM
             | list_num
             | ID




    '''

    if len(p) == 3:
        p[0] = ('EXP', '-', 0, p[2])
    elif type(p[1]) is str:
        if p[1][:2]=="Hx" or p[1][:2]=="HX":
            p[0] = int(p[1][2:],16)
        else:
            p[0] = p[1]
    else:
        p[0] = p[1]


def p_list_num(p):
    '''
    list_num : ID L_SBRACKET type_list_num R_SBRACKET
    '''
    p[0] = ('LIST', p[1], p[3])
def p_set_num(p):
    '''
    set_num : NUMBER COMMA set_num
            | sign_number COMMA set_num
            | NUMBER
            | sign_number
    '''
    if(len(p) > 2):
        p[0] = ('index', p[1], p[3])
    else:
        p[0] = ('index', p[1], None)

# VAR statement
def p_var_stm(p):
    '''
    var_stm : VAR ID ASSIGN_OP exp_stm
            | VAR ID
    '''
    if(len(p) == 3):
        p[0] = ('VAR', p[2], '0')
    else :
        p[0] = ('VAR', p[2], p[4])

def p_var_stm_list(p):
    '''
    var_stm :  VAR ID L_SBRACKET NUMBER R_SBRACKET ASSIGN_OP L_CURLYBRACKET set_num R_CURLYBRACKET
            |  VAR ID L_SBRACKET NUMBER R_SBRACKET
    '''
    if(len(p) == 6):
        p[0] = ('VAR_LIST', p[2], str(p[4]), 'none')
    else :
        p[0] = ('VAR_LIST_VALUE', p[2], str(p[4]), p[8])


# Assignment statement
def p_assign_stm(p):
    '''
    assign_stm : ID ASSIGN_OP exp_stm
    '''
    p[0] = ('ASSIGN', p[1], p[3])

def p_assign_list_stm(p):
    '''
    assign_list_stm : list_num ASSIGN_OP exp_stm
    '''
    p[0] = ('ASSIGN_LIST', p[1], p[3])


def p_exp_stm(p):
    '''exp_stm : exp_stm ADD_OP exp_stm
                | exp_stm MINUS_OP exp_stm
                | exp_stm MUL_OP exp_stm
                | exp_stm DIVIDE_OP exp_stm
                | exp_stm MOD_OP exp_stm
                | L_BRACKET exp_stm R_BRACKET
                | MINUS_OP L_BRACKET exp_stm R_BRACKET
                | type_num
    '''

    if(len(p) == 4):
        if(p[1] == '('):
            p[0] = ('PAREN',p[1],p[2],p[3])
        else:
            p[0] = ('EXP', p[2], p[1], p[3])
    elif(len(p) == 5):
        p[0] = ('MINUS_PAREN', p[2], p[3], p[4])
    else:
        p[0] = p[1]

# IF statement
def p_if_stm(p):
    '''
    if_stm      :  IF condition QUEST EOL L_CURLYBRACKET stm                R_CURLYBRACKET
                |  IF condition QUEST L_CURLYBRACKET     stm                R_CURLYBRACKET
    if_stm_loop :  IF condition QUEST EOL L_CURLYBRACKET inside_loop_stm    R_CURLYBRACKET
                |  IF condition QUEST L_CURLYBRACKET     inside_loop_stm    R_CURLYBRACKET

    '''
    if len(p) == 8:
        p[0] = ('IF', p[2], p[6])
    else :
        p[0] = ('IF', p[2], p[5])


def p_condition_LE(p):
    'condition : type_if_num LE_OP type_if_num'
    p[0] = ('LE_OP', p[1], p[3])

def p_condition_GE(p):
    'condition : type_if_num GE_OP type_if_num'
    p[0] = ('GE_OP', p[1], p[3])

def p_condition_less(p):
    '''condition : type_if_num LT_OP type_if_num'''
    p[0] = ('LT_OP', p[1], p[3])

def p_condition_great(p):
    '''condition : type_if_num GT_OP type_if_num'''
    p[0] = ('GT_OP', p[1], p[3])

def p_condition_EQ(p):
    '''condition : type_if_num EQ_OP type_if_num'''
    p[0] = ('EQ_OP', p[1], p[3])

def p_condition_NE(p):
    '''condition : type_if_num NE_OP type_if_num'''
    p[0] = ('NE_OP', p[1], p[3])

# LOOP statement
def p_loop_stm(p):
    '''
    loop_stm : LOOP L_BRACKET type_num COMMA type_num  R_BRACKET EOL L_CURLYBRACKET  inside_loop_stm  R_CURLYBRACKET
             | LOOP L_BRACKET type_num COMMA type_num  R_BRACKET  L_CURLYBRACKET  inside_loop_stm  R_CURLYBRACKET
             | LOOP L_BRACKET INF R_BRACKET EOL L_CURLYBRACKET  inside_loop_stm  R_CURLYBRACKET
             | LOOP L_BRACKET INF R_BRACKET L_CURLYBRACKET  inside_loop_stm  R_CURLYBRACKET
    '''

    if len(p) == 11 :
        p[0] = ('LOOP', (p[3], p[5]), p[9])
    elif len(p) == 10:
        p[0] = ('LOOP', (p[3], p[5]), p[8])
    elif len(p) == 9:
        p[0] = ('LOOP', p[3], p[7])
    else :
        p[0] = ('LOOP', p[3], p[6])

def p_loop_stm_error(p):
    '''
    loop_stm : LOOP L_BRACKET type_num COMMA type_num  error L_CURLYBRACKET  inside_loop_stm  R_CURLYBRACKET
             | LOOP L_BRACKET INF error L_CURLYBRACKET  inside_loop_stm  R_CURLYBRACKET
    '''
    if len(p) == 10:
        errline = p.lineno(6)
        print("Syntax error in LOOP statement. Bad expression at line:",errline,  " '%s'"% p[7])
    else :
        errline = p.lineno(4)
        print("Syntax error in LOOP statement. Bad expression at line:",errline,  " '%s'"% p[5])

# SHOW statement
def p_showln_var_stm(p):
    '''
    show_stm : SHOWLN L_BRACKET rec_var_msg1_showln R_BRACKET
    '''
    p[0] = ('SHOWLN', '"%lld"', p[3])


def p_showln_str_stm(p):
    '''
    show_stm : SHOWLN L_BRACKET STRING recursive_showln R_BRACKET
    '''
    if(len(p) == 6):
        p[0] = ('SHOWLN', p[3], p[4])

def p_showln_blank_stm(p) :
    '''
    show_stm : SHOWLN L_BRACKET recursive_show R_BRACKET
    '''
    # p[0] = ('SHOWLN', None, None)
    p[0] = ('SHOWLN', '""', p[3])

def p_showln_hex_stm(p):
    '''
    show_stm : SHOWLN L_BRACKET rec_hex_msg1_showln recursive_showln R_BRACKET
    '''
    p[0] = ('SHOWLN', '"%lX"', p[3])

def p_show_var_stm(p):
    '''
    show_stm : SHOW L_BRACKET rec_var_msg1 R_BRACKET
    '''
    p[0] = ('SHOW', '"%lld"', p[3])

def p_show_str_stm(p):
    '''
    show_stm : SHOW L_BRACKET STRING recursive_show R_BRACKET
    '''
    if(len(p) == 6):
        p[0] = ('SHOW', p[3], p[4])

def p_show_hex_stm(p):
    '''
    show_stm : SHOW L_BRACKET hex_msg1 recursive_show R_BRACKET
    '''
    p[0] = ('SHOW', '"%lX"', p[3])

def p_show_pass_rec_msg(p):
    '''
    recursive_show : ADD_OP rec_msg
                  | ADD_OP rec_var_msg2
                  | ADD_OP rec_hex_msg2
                  | empty
    recursive_showln : ADD_OP rec_msg_showln
                         | ADD_OP rec_var_msg2_showln
                         | ADD_OP rec_hex_msg2_showln
                         | empty
    '''
    if(len(p) == 2):
        p[0] = p[0] = ("RECURSIVE_MSG", None, None)
    else:
        p[0] = p[2]

def p_show_rec_hex_msg1(p):
    '''
    hex_msg1 : HEX L_BRACKET type_hex_num R_BRACKET recursive_show
             | hex L_BRACKET type_hex_num R_BRACKET recursive_show
    '''
    p[0] = ("RECURSIVE_MSG",p[3], p[5])

def p_show_rec_hex_msg2(p):
    '''
    rec_hex_msg2 : hex_msg1
    '''
    if(len(p) == 2):
        p[0] = ("SHOW",'"%lX"', p[1])
    else :
        p[0] = ("RECURSIVE_MSG", None, None)

def p_show_rec_str_msg(p):
    '''
    rec_msg : STRING recursive_show
    '''
    if(len(p) == 3):
        p[0] = ("SHOW",p[1], p[2])
    else :
        p[0] = ("RECURSIVE_MSG", None, None)

def p_show_rec_var_msg1(p):
    '''
    rec_var_msg1 : type_var_num recursive_show
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
        p[0] = ("SHOW",'"%lld"', p[1])
    else :
        p[0] = ("RECURSIVE_MSG", None, None)

def p_show_rec_str_msg_showln(p):
    '''
    rec_msg_showln : STRING recursive_showln
    '''
    if(len(p) == 3):
        p[0] = ("SHOWLN",p[1], p[2])
    else :
        p[0] = ("RECURSIVE_MSG", None, None)

def p_show_rec_var_msg1_showln(p):
    '''
    rec_var_msg1_showln : type_var_num recursive_showln
    '''
    if(len(p) == 3):
        p[0] = ("RECURSIVE_MSG",p[1], p[2])
    else :
        p[0] = ("RECURSIVE_MSG", None, None)

def p_show_rec_var_msg2_showln(p):
    '''
    rec_var_msg2_showln : rec_var_msg1_showln
    '''
    if(len(p) == 2):
        p[0] = ("SHOWLN",'"%lld"', p[1])
    else :
        p[0] = ("RECURSIVE_MSG", None, None)

def p_show_rec_hex_msg1_showln(p):
    '''
    rec_hex_msg1_showln : HEX L_BRACKET type_hex_num R_BRACKET recursive_showln
                        | hex L_BRACKET type_hex_num R_BRACKET recursive_showln
    '''
    p[0] = ("RECURSIVE_MSG",p[3], p[5])

def p_show_rec_hex_msg2_showln(p):
    '''
    rec_hex_msg2_showln : rec_hex_msg1_showln
    '''
    if(len(p) == 2):
        p[0] = ("SHOWLN",'"%lX"', p[1])
    else :
        p[0] = ("RECURSIVE_MSG", None, None)


# BREAK statement
def p_break_stm (p):
    '''break_stm : BREAK'''
    p[0] = ('BREAK', None, None)

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
    if not p:
        print("Syntax ERROR AT EOF")
    else:
        print("Syntax ERROR : '%s' at line '%s'" % (p.value,p.lineno))
    sys.exit(1)

hparser = yacc.yacc()

lines = open("test.halt", 'r').read()
tree = hparser.parse(lines)
# print(tree)




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
