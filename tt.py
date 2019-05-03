import sys
import platform
from inspect import getframeinfo, stack
import haltlex as lex

system_platform = platform.system()

if system_platform == 'Linux':
    asmheader = "DEFAULT REL\nextern printf\nextern scanf\nextern fflush\nglobal main\n"
    main_entry = 'main:'
    scanf_label = 'scanf'
    printf_label = 'printf'
    fflush_label = 'fflush'
elif system_platform == 'Darwin':
    asmheader = "DEFAULT REL\nextern _printf\nextern _scanf\nextern _fflush\nglobal _main\n"
    main_entry = '_main:'
    scanf_label = '_scanf'
    printf_label = '_printf'
    fflush_label = '_fflush'
else:
    # print('Warning : Windows assembly is not supported yet. Fallback to Linux')
    asmheader = "DEFAULT REL\nextern printf\nextern scanf\nextern fflush\nglobal main\n"
    main_entry = 'main:'
    scanf_label = 'scanf'
    printf_label = 'printf'
    fflush_label = 'fflush'


asmtext = "section .text\n"
asmdata = 'section .data\n'
asmleave = 'mov rax, 0\npop rbp\nret\n'

# reg_order = ["rdi", "rsi", "rdx", "rcx"]
reg_order = ["rcx", "rdx", "r8", "r9"]

global_var = []
global_arr = []

var_loop = ["_VL1" , "_VL2", "_VL3","_VL4","_VL5"]
vare_loop = ["_VEL1" , "_VEL2", "_VEL3","_VEL4","_VEL5"]
fun_loop = ["_L1","_L2","_L3","_L4","_L5"]
nvl = -1
nfl = -1

# asmdata += "%s dq %s\n" % (chBreak, 1)
asmdata += "%s dq %s\n" % (var_loop[0], 0)
asmdata += "%s dq %s\n" % (var_loop[1], 0)
asmdata += "%s dq %s\n" % (var_loop[2], 0)
asmdata += "%s dq %s\n" % (var_loop[3], 0)
asmdata += "%s dq %s\n" % (var_loop[4], 0)

asmdata += "%s dq %s\n" % (vare_loop[0], 0)
asmdata += "%s dq %s\n" % (vare_loop[1], 0)
asmdata += "%s dq %s\n" % (vare_loop[2], 0)
asmdata += "%s dq %s\n" % (vare_loop[3], 0)
asmdata += "%s dq %s\n" % (vare_loop[4], 0)

global_str_counter = 0
global_str = {}
global_if_counter = 0
str_prefix = '_LC'

lexer = lex.lexer

def add_data(var_name, value):
    global asmdata
    asmdata += "%s db %s\n" % (var_name, value)


def add_text(cmd):
    global asmtext
    asmtext += cmd + '\n'


# init

add_data("NewLine","\"\",10, 0")
# sys_input
# add_data("_fmin", "\"%ld\", 0")
# add_text("_input:")
# add_text("push rbp")
# add_text("mov rbp, rsp")
# add_text("sub rsp, 16")
# add_text("lea rax, [rbp - 8]")
# add_text("mov rsi, rax")
# add_text("mov rdi, _fmin")
# add_text("call " + scanf_label)
# add_text("mov rax, [rbp - 8]")
# add_text("leave")
# add_text("ret")

# add main label
add_text(main_entry)
add_text("push rbp")


cmp_symbol = ['EQ_OP', '!=', 'GT_OP', 'LT_OP', 'GE_OP', 'LE_OP', '&&']


def get_type(symbol):

    if type(symbol) is tuple:
        if symbol[0] == 'LIST':
            return 'ARRAY'
        return 'expression'
    if symbol == 'LIST':
        return 'ARRAY'
    if symbol == 'input':
        return 'INPUT'
    try:
        int(symbol)
        return 'CONSTANT'
    except ValueError:
        return 'ID'


def get_var(symbol):
    if symbol in global_var:
        return symbol
    print_error("Use of undeclare variable %s" % symbol)

def get_arr(ID,num):
    for i in global_arr :
        if (i[0]==ID and int(num)>=0 and num<int(i[1])):
                return ID
    print_error("out of range '%s' " % ID)


def get_str(text):
    if text not in global_str:
        declare_string(text)
    return global_str[text]


def print_error(error_str, show_line=True):
    if show_line:
        print("ERROR : %s at line %d" % (error_str, lexer.lineno)) #fail number
    else:
        print("ERROR : %s" % error_str)
    sys.exit(1)


def error_token():
    # caller = getframeinfo(stack()[1][0])
    # print("Error line : " + str(caller.lineno))
    print_error("Unexpected token")


def declare_var(var_name, value=0):
    global asmdata
    if var_name in global_var:
        print_error("Duplicate variable",show_line=True)
    else:
        global_var.append(var_name)
        val_type = get_type(value)
        if val_type == 'INPUT':
            asmdata += "%s dq 0\n" % var_name
            input_routine()
            add_text("mov [%s], rax" % var_name)
        elif val_type == 'CONSTANT':
            asmdata += "%s dq %s\n" % (var_name, value)
            # print("CONSTANT")
        elif val_type == 'ARRAY':
            asmdata += "%s dq 0\n" % var_name
            assign_routine(var_name, value)
        elif val_type == 'expression':
            asmdata += "%s dq 0\n" % var_name
            statement_main( ('ASSIGN', var_name, value ))
            # print("VAR CONSTANT")
        elif val_type == 'ID':
            asmdata += "%s dq 0\n" % var_name
            statement_main( ('ASSIGN', var_name, value ))
            # print("VAR ID")
        else:
            print_error('Declare variable with unsupport type.',
                        show_line=False)


def declare_string(text):
    global global_str_counter
    if text not in global_str:
        asm_symbol = str_prefix + str(global_str_counter)
        global_str[text] = asm_symbol
        _text = ''
        if '\\n' in text:
            texts = text.replace('"', '').split('\\n')
            for t in texts:
                if t:
                    _text += '"' + t + '", 10,'
            _text += ' 0'
        else:
            _text = text + ', 0'
        add_data(asm_symbol, _text)
        global_str_counter += 1


def declare_arr(var_name, args, index):
    global asmdata
    i = 0
    if var_name in global_var:
        print_error("Duplicate variable at declare array",show_line=True)
    else:
        global_var.append(var_name)
        if index[0] == 'index':
            asmdata += "%s dq " % var_name
            while index[2] != None:
                asmdata += "%s" % index[1]
                i+=1
                if index[2] != 'None':
                    asmdata += ","
                    index = index[2]
                else:
                    index[0]='None'
            asmdata += "%s" % index[1]
            i+=1
            if i!=(int)(args):
                print_error("Declare array invalid '%s'" % var_name)
        else:
            # var array with size
            asmdata += "%s times %s dq 0" % (var_name, args)
        global_arr.append([var_name,args])
        asmdata += '\n'


def multiple_stm_routine(stm1, stm2):
    statement_main(stm1)
    statement_main(stm2)


def if_routine(exp, stm):
    global global_if_counter
    global_if_counter += 1
    exit_c = global_if_counter
    expression_if(exp)
    statement_main(stm)

    print("ENDIF")
    add_text("_EXIF%d:" % exit_c)



def getValueVarible(ex):
    type_a = get_type(ex)

    if type_a == 'ID':
        get_var(ex)
        add_text("mov rax, [%s]" % ex)
        return "rax"
    elif type_a == 'CONSTANT':
        print("rax")
        add_text("mov rax, %s" % ex)
        return 'rax'
    elif type_a == 'ARRAY':
        get_var(ex[1])
        index_type = get_type(ex[2])
        if index_type == 'ID':
            get_var(ex[2])
            add_text('mov rbx, [%s]' % ex[2])
            add_text('mov rax,[%s+rbx*8]' % (ex[1]))
            return 'rax'
        elif index_type == 'CONSTANT':
            get_arr(ex[1],ex[2])
            add_text('mov rax, [%s + %s * 8]' %( ex[1], ex[2]))
            return 'rax'

# reg_order = ["rcx", "rdx", "r8", "r9"]
def loop_routing(exp, stm):
    global nvl,nfl,var_loop,fun_loop,chBreak
    nvl+=1
    nfl+=1
    if(exp != 'INF'):
        print("!INF")
        b=getValueVarible(exp[1])

        add_text("mov rcx, %s" % (b))
        add_text("mov [%s], rcx" % (var_loop[nvl]))

        a=getValueVarible(exp[0])
        add_text("mov rcx, %s" % (a))
        add_text("mov [%s], rcx" % (vare_loop[nvl]))

        add_text("%s:" % (fun_loop[nfl]))

        if stm != None:
            statement_main(stm)

        add_text("mov rcx, [%s]"% (var_loop[nvl]))
        add_text("dec rcx")
        add_text("mov [%s], rcx"% (var_loop[nvl]))
        add_text("mov rax, [%s]"% (vare_loop[nvl]))
        add_text("cmp rcx, rax")
        add_text("je %sEX"% (fun_loop[nfl]))
        add_text("jmp %s"% (fun_loop[nfl]))
        add_text("%sEX:"% (fun_loop[nfl]))
        fun_loop[nfl]='_'+fun_loop[nfl]

    if exp == 'INF':
        print("INFFFFFF")
        add_text("mov rcx, %d" % (1))
        add_text("mov [%s], rcx" % (var_loop[nvl]))
        add_text("%s:" % (fun_loop[nfl]))

        if stm != None:
            statement_main(stm)

        add_text("jmp %s"% (fun_loop[nfl]))
        add_text("%sEX:"% (fun_loop[nfl]))
        fun_loop[nfl]='_'+fun_loop[nfl]

    nvl=nvl-1
    nfl=nfl-1

def break_loop():
    global nvl,nfl,var_loop,fun_loop,chBreak
    # add_text("mov [%s], 0"% (chBreak))
    # add_text("mov rcx, [%s]"% (chBreak))
    # add_text("mov [%s], 1"% (chBreak))
    # add_text("cmp rcx, 0")
    add_text("jmp %sEX"% (fun_loop[nfl]))



def statement_main(stm):
    try:
        state_symbol = stm[0]
        switcher = {
            'ASSIGN': assign_routine,
            'ASSIGN_LIST': assign_routine,
            'SHOW': print_routine,
            'SHOWLN': print_routine,
            'VAR': declare_var,
            'VAR_LIST': declare_arr,
            'MULTIPLE_LINE': multiple_stm_routine,
            'IF': if_routine,
            'LOOP': loop_routing,
            'VAR_LIST_VALUE': declare_arr,
            'BREAK': break_loop
        }
        func = switcher[state_symbol]
        if stm[0]=='BREAK':
            func()
        elif stm[0] == 'VAR_LIST' or stm[0] == 'VAR_LIST_VALUE':
            func(stm[1],stm[2],stm[3])
        elif stm[0]=='SHOWLN':
            func(stm[1], stm[2],True)
        elif stm[0]=='SHOW':
            func(stm[1], stm[2])
        else:
            func(stm[1], stm[2])

    except SystemExit:
        sys.exit(1)
    except:
        pass

def expression_if(exp, count=0):
    t = exp[0]
    if t in cmp_symbol:
        cmp_main(exp)

def expression_main(exp, count=0):
    # print(exp[0])
    t = exp[1]
    if t in cmp_symbol:
        cmp_main(exp)
    else:
        switcher = {
            '+': plus_routine,
            '-': minus_routine,
            '*': multiply_routine,
            '/': divide_routine,
            '%': mod_routine,
            '(': paren_routine
        }
        func = switcher[t]
        if t=='(' and exp[0]=='MINUS_PAREN':
            minus_routine(0,exp[2])
        elif t=='(' and get_type(exp[2])=='CONSTANT':
            paren_alone_routine(exp[2])
        elif t=='(' and get_type(exp[2])=='ID':
            paren_alone_ID_routine(exp[2])
        elif t=='(' and get_type(exp[2])=='ARRAY':
            paren_alone_LIST_routine(exp[2])
        elif t=='(':
            func(exp[2],0)
        else:
            func(exp[2], exp[3], count)

def paren_routine(a,count=0):
    expression_main(a,count)

def paren_alone_routine(a):
    add_text("mov rax, %s" % a)
def paren_alone_ID_routine(a):
    add_text("mov rax, [%s]" % a)
def paren_alone_LIST_routine(a):
    add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))

def cmp_main(cmp_e):
    global global_if_counter
    t = cmp_e[0]
    a = cmp_e[1]
    b = cmp_e[2]
    type_a = get_type(a)
    type_b = get_type(b)
    if type_a == 'expression':
        expression_main(a)
    elif type_a == 'ID':
        get_var(a)
        add_text("mov rax, [%s]" % a)
    elif type_a == 'CONSTANT':
        add_text("mov rax, %s" % a)
    elif type_a == 'ARRAY':
        index_type = get_type(a[2])
        get_var(a[1])
        if index_type == 'ID':
            get_var(a[2])
            add_text('mov rbx, %s' % a[1])
            add_text('mov rcx, [%s]' % a[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_text('mov rax, [rbx]')
        elif index_type == 'CONSTANT':
            get_arr(a[1],a[2])
            add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))
        else:
            error_token()

    if type_b == 'expression':
        expression_main(b)
    elif type_b == 'ID':
        get_var(b)
        add_text("mov rbx, [%s]" % b)
    elif type_b == 'CONSTANT':
        add_text("mov rbx, %s" % b)
    elif type_a == 'ARRAY':
        index_type = get_type(b[2])
        get_var(a[1])
        if index_type == 'ID':
            get_var(a[2])
            add_text('mov rbx, %s' % b[1])
            add_text('mov rcx, [%s]' % b[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_text('mov rbx, [rbx]')
        elif index_type == 'CONSTANT':
            get_arr(a[1],a[2])
            add_text('mov rbx, [%s + %s * 8]' % (b[1], b[2]))
        else:
            error_token()

    if t != '&&':
        add_text("cmp rax, rbx")
        switcher = {
        'EQ_OP': equal_routine,
        'GT_OP': greater_routine,
        'LT_OP': less_routine,
        'LE_OP': less_equ_routine,
        'GE_OP': greater_equ_routine,
        '&&': and_routine
    }
    func = switcher[t]
    func()


def input_routine():
    add_text("call _input")


def print_routine(fmt, arg,enter=False,count=0):
    # print("mov rcx, " + get_str(fmt),fmt)
    # print("len "+fmt+str(len(fmt)-2))
    count += len(fmt)-2
    if count > 255 :
        print_error("String is too long (255)")
    add_text("mov rcx, " + get_str(fmt))
    reg_c = 1
    while arg[1] != None :
        if arg[0] == 'RECURSIVE_MSG':
            a = arg[1]
            a_type = get_type(a)
            if a_type == 'CONSTANT':
                add_text("mov %s, %s" % (reg_order[reg_c], a))
            elif a_type == 'ID':
                get_var(a)
                add_text("mov %s, [%s]" % (reg_order[reg_c], a))
            elif a_type == 'ARRAY':
                get_var(a[1])
                index_type = get_type(a[2])
                if index_type == 'ID':
                    get_var(a[2])
                    add_text('mov rbx, [%s]' % a[2])
                    add_text('mov %s, [%s+rbx*8]' % (reg_order[reg_c],a[1]))
                elif index_type == 'CONSTANT':
                    get_arr(a[1],a[2])
                    add_text('mov %s, [%s + %s * 8]' %
                             (reg_order[reg_c], a[1], a[2]))
            else:
                print("no Argument")
                expression_main(arg[1])
                add_text("mov %s, rax" % reg_order[reg_c])
        if arg[0] == 'SHOW'or arg[0] == 'SHOWLN':
            # print("BREAK -> print"+arg[1])
            if arg[0] == 'SHOWLN':
                enter=True
            break
        reg_c += 1
        arg = arg[2]
        

    add_text("call " + printf_label)
    # print("call printf"+str(arg[0]))
    if arg[1]==None and enter==True:
        add_text("mov rcx ,NewLine")
        add_text("call " + printf_label)
                
    # add_text("xor rcx, rcx")
    # add_text("call " + fflush_label)            

    if arg[0]=='SHOW'or arg[0] == 'SHOWLN':
        if arg[0] == 'SHOWLN':
            print_routine(arg[1],arg[2],True,count)
        else:
            print_routine(arg[1],arg[2],False,count)



def assign_routine(dest, source):
    global global_var
    d_type = get_type(dest)
    s_type = get_type(source)
    print("sss"+str(dest))
    if s_type == 'CONSTANT':
        add_text('mov rax, ' + str(source))
    elif s_type == 'ID':
        get_var(source)
        add_text('mov rax, [%s]' % source)
    elif s_type == 'expression':
        expression_main(source)
    elif s_type == 'INPUT':
        input_routine()
    elif s_type == 'ARRAY':
        index_type = get_type(source[2])
        get_var(source[1])
        if index_type == 'ID':
            get_var(source[2])
            add_text('mov rbx, %s' % source[1])
            add_text('mov rcx, [%s]' % source[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_text('mov rax, [rbx]')
        elif index_type == 'CONSTANT':
            get_arr(source[1],source[2])
            add_text('mov rax, [%s + %s * 8]' % (source[1], source[2]))

    if d_type == 'ARRAY':
        index_type = get_type(dest[2])
        if index_type == 'ID':
            get_var(dest[1])
            add_text('mov rbx, %s' % dest[1])
            add_text('mov rcx, [%s]' % dest[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_text('mov [rbx], rax')
        elif index_type == 'CONSTANT':
            get_arr(dest[1], dest[2])
            add_text('mov [%s + %s * 8], rax' % (dest[1], dest[2]))
    else:
        get_var(dest)
        add_text('mov [%s], rax' % dest)


def plus_routine(a, b, count=0):
    a_type = get_type(a)
    b_type = get_type(b)
    if a_type == 'CONSTANT':
        if count == 0:
            add_text("mov rax, %s" % a)
        else:
            add_text("add rax, %s" % a)
    elif a_type == 'ID':
        get_var(a)
        if count == 0:
            add_text("mov rax, [%s]" % a)
        else:
            add_text("add rax, [%s]" % a)
    elif a_type == 'expression':
        expression_main(a, count)
    elif a_type == 'ARRAY':
        index_type = get_type(a[2])
        if index_type == 'ID':
            get_var(a[2])
            add_text('mov rbx, %s' % a[1])
            add_text('mov rcx, [%s]' % a[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            if count == 0:
                add_text('mov rax, [rbx]')
            else:
                add_text('add rax, [rbx]')
        elif index_type == 'CONSTANT':
            get_arr(a[1], a[2])
            if count == 0:
                add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))
            else:
                add_text('add rax, [%s + %s * 8]' % (a[1], a[2]))
    else:
        error_token()

    count += 1
    if b_type == 'CONSTANT':
        add_text("add rax, %s" % b)
    elif b_type == 'ID':
        get_var(b)
        add_text("add rax, [%s]" % b)
    elif b_type == 'expression':
        add_text("push rax")
        expression_main(b, count)
        add_text("pop rbx")
        add_text("add rax,rbx")
    elif b_type == 'ARRAY':
        index_type = get_type(b[2])
        if index_type == 'ID':
            get_var(b[2])
            add_text('mov rbx, %s' % b[1])
            add_text('mov rcx, [%s]' % b[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_text('add rax, [rbx]')
        elif index_type == 'CONSTANT':
            get_arr(b[1], b[2])
            add_text('add rax, [%s + %s * 8]' % (b[1], b[2]))

    else:
        error_token()

def minus_routine(a, b, count=0):
    global asmtext
    a_type = get_type(a)
    b_type = get_type(b)
    if a_type == 'CONSTANT':
        if count == 0:
            add_text("mov rax, %s" % a)
        else:
            add_text("sub rax, %s" % a)
    elif a_type == 'ID':
        get_var(a)
        if count == 0:
            add_text("mov rax, [%s]" % a)
        else:
            add_text("sub rax, [%s]" % a)
    elif a_type == 'expression':
        expression_main(a, count)
    elif a_type == 'ARRAY':
        index_type = get_type(a[2])
        if index_type == 'ID':
            get_var(a[2])
            add_text('mov rbx, %s' % a[1])
            add_text('mov rcx, [%s]' % a[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            if count == 0:
                add_text('mov rax, [rbx]')
            else:
                add_text('sub rax, [rbx]')
        elif index_type == 'CONSTANT':
            get_arr(a[1],a[2])
            if count == 0:
                add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))
            else:
                add_text('sub rax, [%s + %s * 8]' % (a[1], a[2]))
    else:
        error_token()

    count += 1


    if b_type == 'CONSTANT':
        add_text("sub rax, %s" % b)
    elif b_type == 'ID':
        get_var(b)
        add_text("sub rax, [%s]" % b)
    elif b_type == 'expression':
        add_text("push rax")
        expression_main(b, count)
        add_text("mov rbx,rax")
        add_text("pop rax")
        add_text("sub rax,rbx")
    elif b_type == 'ARRAY':
        index_type = get_type(b[2])
        if index_type == 'ID':
            get_var(b[2])
            add_text('mov rbx, %s' % b[1])
            add_text('mov rcx, [%s]' % b[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_text('sub rax, [rbx]')
        elif index_type == 'CONSTANT':
            get_arr(b[1], b[2])
            add_text('sub rax, [%s + %s * 8]' % (b[1], b[2]))
    else:
        error_token()


def multiply_routine(a, b, count=0):
    a_type = get_type(a)
    b_type = get_type(b)
    if a_type == 'CONSTANT':
        if count == 0:
            add_text("mov rax, %s" % a)
        else:
            add_text("mov rax, %s" % a)
    elif a_type == 'ID':
        get_var(a)
        if count == 0:
            add_text("mov rax, [%s]" % a)
        else:
            add_text("mov rax, [%s]" % a)
    elif a_type == 'expression':
        expression_main(a, count)
    elif a_type == 'ARRAY':
        index_type = get_type(a[2])
        if index_type == 'ID':
            get_var(a[2])
            add_text('mov rbx, %s' % a[1])
            add_text('mov rcx, [%s]' % a[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            if count == 0:
                add_text('mov rax, [rbx]')
            else:
                add_text('mov rax, [rbx]')
                # add_text('imul rax, [rbx]')
        elif index_type == 'CONSTANT':
            get_arr(a[1], a[2])
            if count == 0:
                add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))
            else:
                add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))
    else:
        error_token()
    count += 1

    if b_type == 'CONSTANT':
        add_text("imul rax, %s" % b)
    elif b_type == 'ID':
        get_var(b)
        add_text("imul rax, [%s]" % b)
    elif b_type == 'expression':
        add_text("push rax")
        expression_main(b, count)
        add_text("pop rbx")
        add_text('imul rax, rbx')
    elif b_type == 'ARRAY':
        index_type = get_type(b[2])
        if index_type == 'ID':
            get_var(b[2])
            add_text('mov rbx, %s' % b[1])
            add_text('mov rcx, [%s]' % b[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_text('imul rax, [rbx]')
        elif index_type == 'CONSTANT':
            get_arr(b[1], b[2])
            add_text('imul rax, [%s + %s * 8]' % (b[1], b[2]))
    else:
        error_token()


def divide_routine(a, b, count=0):
    a_type = get_type(a)
    b_type = get_type(b)
    add_text('xor rdx, rdx')
    if a_type == 'CONSTANT':
        if count == 0:
            add_text("mov rax,  %s" % a)
        else:
            add_text("mov rax,  %s" % a)
            # add_text('idiv rcx')
    elif a_type == 'ID':
        get_var(a)
        if count == 0:
            add_text('mov rax, [%s]' % a)
        else:
            add_text('mov rax, [%s]' % a)
            # add_text('mov rcx, [%s]' % a)
            # add_text('idiv rcx')
    elif a_type == 'expression':
        expression_main(a, count)
    elif a_type == 'ARRAY':
        index_type = get_type(a[2])
        if index_type == 'ID':
            get_var(a[2])
            add_text('mov rbx, %s' % a[1])
            add_text('mov rcx, [%s]' % a[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            if count == 0:
                add_text('mov rax, [rbx]')
            else:
                add_text('mov rax, [rbx]')
                # add_text('mov rcx, [rbx]')
                # add_text('idiv rcx')
        elif index_type == 'CONSTANT':
            get_arr(a[1], a[2])
            if count == 0:
                add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))
            else:
                add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))
                # add_text('mov rcx, [%s + %s * 8]' % (a[1], a[2]))
                # add_text('idiv rcx')
    else:
        error_token()
    count += 1

    add_text('xor rdx, rdx')
    if b_type == 'CONSTANT':
        add_text('mov rcx, %s' % b)
        add_text('idiv rcx')
    elif b_type == 'ID':
        get_var(b)
        add_text('mov rcx, [%s]' % b)
        add_text('idiv rcx')
    elif b_type == 'expression':
        add_text("push rax")
        expression_main(b, count)
        add_text("mov rcx, rax")
        add_text("pop rbx")
        add_text("mov rax, rbx")
        add_text('idiv rcx')
    elif b_type == 'ARRAY':
        index_type = get_type(b[2])
        if index_type == 'ID':
            get_var(b[2])
            add_text('mov rbx, %s' % b[1])
            add_text('mov rcx, [%s]' % b[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_data('mov rcx, [rbx]')
            add_text('idiv rcx')
        elif index_type == 'CONSTANT':
            get_arr(b[1], b[2])
            add_text('mov rcx, [%s + %s * 8]' % (b[1], b[2]))
            add_text('idiv rcx')
    else:
        error_token()


def mod_routine(a, b, count=0):
    a_type = get_type(a)
    b_type = get_type(b)
    add_text('xor rdx, rdx')
    if a_type == 'CONSTANT':
        if count == 0:
            add_text("mov rax,  %s" % a)
        else:
            add_text("mov rax,  %s" % a)
    elif a_type == 'ID':
        get_var(a)
        if count == 0:
            add_text('mov rax, [%s]' % a)
        else:
            add_text("mov rax,  %s" % a)
            # add_text('mov rcx, [%s]' % a)
            # add_text('idiv rcx')
            # add_text('mov rax, rdx')
    elif a_type == 'expression':
        expression_main(a, count)
    elif a_type == 'ARRAY':
        index_type = get_type(a[2])
        if index_type == 'ID':
            get_var(a[2])
            add_text('mov rbx, %s' % a[1])
            add_text('mov rcx, [%s]' % a[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            if count == 0:
                add_text('mov rax, [rbx]')
            else:
                add_text('mov rax, [rbx]')
                # add_text('mov rcx, [rbx]')
                # add_text('idiv rcx')
                # add_text('mov rax, rdx')
        elif index_type == 'CONSTANT':
            get_arr(a[1], a[2])
            if count == 0:
                add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))
            else:
                add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))
                # add_text('mov rcx, [%s + %s * 8]' % (a[1], a[2]))
                # add_text('idiv rcx')
                # add_text('mov rax, rdx')
    else:
        error_token()

    count += 1

    add_text('xor rdx, rdx')
    if b_type == 'CONSTANT':
        add_text('mov rcx, %s' % b)
        add_text('idiv rcx')
        add_text('mov rax, rdx')
    elif b_type == 'ID':
        get_var(b)
        add_text('mov rcx, [%s]' % b)
        add_text('idiv rcx')
        add_text('mov rax, rdx')
    elif b_type == 'expression':
        add_text("push rax")
        expression_main(b, count)
        add_text("mov rcx, rax")
        add_text("pop rbx")
        add_text("mov rax, rbx")
        add_text('idiv rcx')
        add_text("mov rax, rdx")
    elif b_type == 'ARRAY':
        index_type = get_type(b[2])
        if index_type == 'ID':
            get_var(b[2])
            add_text('mov rbx, %s' % b[1])
            add_text('mov rcx, [%s]' % b[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_data('mov rcx, [rbx]')
            add_text('idiv rcx')
            add_text('mov rax, rdx')
        elif index_type == 'CONSTANT':
            get_arr(b[1], b[2])
            add_text('mov rcx, [%s + %s * 8]' % (b[1], b[2]))
            add_text('idiv rcx')
            add_text('mov rax, rdx')
    else:
        error_token()


def and_routine():
    pass


def less_equ_routine():
    add_text("jg _EXIF%d" % global_if_counter)


def greater_equ_routine():
    add_text("jl _EXIF%d" % global_if_counter)


def less_routine():
    print("GU")
    add_text("jge _EXIF%d" % global_if_counter)


def greater_routine():
    add_text("jle _EXIF%d" % global_if_counter)


def not_equal_routine():
    add_text("je _EXIF%d" % global_if_counter)


def equal_routine():
    add_text("jne _EXIF%d" % global_if_counter)
