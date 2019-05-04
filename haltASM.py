import sys
import platform
from inspect import getframeinfo, stack
import haltlex as lex

system_platform = platform.system()


asmheader = "DEFAULT REL\nextern printf\nextern scanf\nextern fflush\nglobal main\n"
main_entry = 'main:'
scanf_label = 'scanf'
printf_label = 'printf'
fflush_label = 'fflush'


asmtext = "section .text\n"
asmdata = 'section .data\n'
asmleave = 'mov rax, 0\npop rbp\nret\n'

reg_order = ["rcx", "rdx", "r8", "r9"]

global_var = []
global_arr = []

var_loop = ["_VL1"]
vare_loop = ["_VEL1"]
fun_loop = ["_L1"]
nvl = -1
nfl = -1

asmdata += "%s dq %s\n" % (var_loop[0], 0)
asmdata += "%s dq %s\n" % (vare_loop[0], 0)

global_str_counter = 0
global_str = {}
global_if_counter = 0
str_prefix = '_STR'

# lexer = lex.lexer

def add_data(var_name, value):
    global asmdata
    asmdata += "%s db %s\n" % (var_name, value)


def add_text(cmd):
    global asmtext
    asmtext += cmd + '\n'


# init
add_data("NewLine","\"\",10, 0")
add_text(main_entry)
add_text("push rbp")


cmp_symbol = ['EQ_OP', 'NE_OP', 'GT_OP', 'LT_OP', 'GE_OP', 'LE_OP']


def get_type(symbol):
    if type(symbol) is tuple:
        if symbol[0] == 'LIST':
            return 'ARRAY'
        if symbol[0] =='len':
            return 'LEN'
        return 'EXP'
    if symbol == 'LIST':
        return 'ARRAY'
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
def get_len(ID):
    get_var(ID)
    for i in global_arr :
        if (i[0]==ID):
                add_text("mov rax, %s"%i[1])
                # print("len of "+ID+" : "+i[1])
                return
    add_text("mov rax, 1")
    # print("len of "+ID+" : 1")

def get_num_len(ID):
    get_var(ID)
    for i in global_arr :
        if (i[0]==ID):
            print("len of "+ID+" : "+i[1])
            return i[1]
    print("len of "+ID+" : 1")
    return "1"


def get_str(text):
    if text not in global_str:
        create_string(text)
    return global_str[text]


def print_error(error_str, show_line=True):
    if show_line:
        # print("ERROR : %s at line %d" % (error_str, lexer.lineno)) #fail number
        print("ERROR : %s" % error_str)
    else:
        print("ERROR : %s" % error_str)
    sys.exit(1)


def error_token():
    print_error("Unexpected token")


def create_var(var_name, value=0):
    global asmdata
    if var_name in global_var:
        print_error("Duplicate variable"+var_name,show_line=True)
    else:
        global_var.append(var_name)
        val_type = get_type(value)
        if val_type == 'CONSTANT':
            asmdata += "%s dq %s\n" % (var_name, value)
        elif val_type == 'ARRAY':
            asmdata += "%s dq 0\n" % var_name
            assign_stm(var_name, value)
        elif val_type =="LEN":
            value=get_num_len(value[1])
            asmdata += "%s dq %s\n" % (var_name, value)
        elif val_type == 'EXP':
            asmdata += "%s dq 0\n" % var_name
            main( ('ASSIGN', var_name, value ))
        elif val_type == 'ID':
            asmdata += "%s dq 0\n" % var_name
            main( ('ASSIGN', var_name, value ))
        else:
            print_error('Declare variable with unsupport type.',
                        show_line=False)


def create_string(text):
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


def create_arr(var_name, args, index):
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
            # check array size
            if i!=(int)(args):
                print_error("Declare array invalid '%s'" % var_name)
        else:
            # var array with size
            asmdata += "%s times %s dq 0" % (var_name, args)
        global_arr.append([var_name,args])
        asmdata += '\n'


def multiple_line(stm1, stm2):
    main(stm1)
    main(stm2)


def if_stm(exp, stm):
    global global_if_counter
    global_if_counter += 1
    exit_c = global_if_counter
    exp_if(exp)
    main(stm)

    add_text("_EXIF%d:" % exit_c)



def get_value_var(ex):
    type_a = get_type(ex)

    if type_a == 'ID':
        get_var(ex)
        add_text("mov rax, [%s]" % ex)
        return "rax"
    elif type_a == 'LEN':
        get_len(ex[1])
        return "rax"
    elif type_a == 'EXP':
        exp_main(ex)
        return "rax"
    elif type_a == 'CONSTANT':
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


def loop_stm(exp, stm):
    global nvl,nfl,var_loop,fun_loop,chBreak,asmdata
    nvl+=1
    nfl+=1
    if len(var_loop) < nvl+1 :
        var_loop.append("_VL"+str(nvl+1))
        vare_loop.append("_VEL"+str(nvl+1))
        fun_loop.append("_L"+str(nvl+1))
        asmdata += "%s dq %s\n" % (var_loop[nvl], 0)
        asmdata += "%s dq %s\n" % (vare_loop[nvl], 0)

    if(exp != 'INF'):
        if isinstance(exp[1],int) and isinstance(exp[0],int):
            if exp[0] >= exp[1]:
                print_error("invalid syntax")

        b=get_value_var(exp[1])
        add_text("mov rcx, %s" % (b))
        add_text("mov [%s], rcx" % (var_loop[nvl]))

        a=get_value_var(exp[0])
        add_text("mov rcx, %s" % (a))
        add_text("mov [%s], rcx" % (vare_loop[nvl]))
        add_text("%s:" % (fun_loop[nfl]))

        if stm != None:
            main(stm)

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
        add_text("mov rcx, %d" % (1))
        add_text("mov [%s], rcx" % (var_loop[nvl]))
        add_text("%s:" % (fun_loop[nfl]))

        if stm != None:
            main(stm)

        add_text("jmp %s"% (fun_loop[nfl]))
        add_text("%sEX:"% (fun_loop[nfl]))
        fun_loop[nfl]='_'+fun_loop[nfl]

    nvl=nvl-1
    nfl=nfl-1

def break_loop():
    global nvl,nfl,var_loop,fun_loop,chBreak
    add_text("jmp %sEX"% (fun_loop[nfl]))


def main(stm):
    try:
        state_symbol = stm[0]
        switcher = {
            'ASSIGN': assign_stm,
            'ASSIGN_LIST': assign_stm,
            'SHOW': print_stm,
            'SHOWLN': print_stm,
            'VAR': create_var,
            'VAR_LIST': create_arr,
            'MULTIPLE_LINE': multiple_line,
            'IF': if_stm,
            'LOOP': loop_stm,
            'VAR_LIST_VALUE': create_arr,
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

def exp_if(exp):
    t = exp[0]
    if t in cmp_symbol:
        cmp_main(exp)

def exp_main(exp):
    t = exp[1]
    if t in cmp_symbol:
        cmp_main(exp)
    else:
        switcher = {
            '+': plus_stm,
            '-': minus_stm,
            '*': multiply_stm,
            '/': divide_stm,
            '%': mod_stm,
            '(': paren_stm
        }
        func = switcher[t]
        if t=='(' and exp[0]=='MINUS_PAREN':
            minus_stm(0,exp[2])
        elif t=='(' and get_type(exp[2])=='CONSTANT':
            paren_alone_stm(exp[2])
        elif t=='(' and get_type(exp[2])=='ID':
            paren_alone_ID_stm(exp[2])
        elif t=='(' and get_type(exp[2])=='ARRAY':
            paren_alone_list_stm(exp[2])
        elif t=='(':
            func(exp[2])
        else:
            func(exp[2], exp[3])

def paren_stm(a):
    exp_main(a)

def paren_alone_stm(a):
    add_text("mov rax, %s" % a)
def paren_alone_ID_stm(a):
    add_text("mov rax, [%s]" % a)
def paren_alone_list_stm(a):
    add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))

def cmp_main(cmp_e):
    
    global global_if_counter
    t = cmp_e[0]
    a = cmp_e[1]
    b = cmp_e[2]
    
    type_a = get_type(a)
    type_b = get_type(b)
    
    if type_a == 'EXP':
        exp_main(a)
    elif type_a == 'LEN':
        get_len(a[1])
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

    if type_b == 'EXP':
        add_text('push rax')
        exp_main(b)
        add_text('pop rax')
    elif type_b == 'LEN':
        add_text('push rax')
        get_len(b[1])
        add_text('mov rbx,rax')
        add_text('pop rax')
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
        'EQ_OP': equal_stm,
        'GT_OP': greater_stm,
        'LT_OP': less_stm,
        'LE_OP': less_equ_stm,
        'GE_OP': greater_equ_stm,
        'NE_OP': not_equal_stm
    }
    func = switcher[t]
    func()

def print_stm(fmt, arg,enter=False,count=0):
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
                exp_main(arg[1])
                add_text("mov %s, rax" % reg_order[reg_c])
        if arg[0] == 'SHOW'or arg[0] == 'SHOWLN':
            if arg[0] == 'SHOWLN':
                enter=True
            break
        reg_c += 1
        arg = arg[2]


    add_text("call " + printf_label)
    if arg[1]==None and enter==True:
        add_text("mov rcx ,NewLine")
        add_text("call " + printf_label)
    # add_text("xor rcx, rcx")
    # add_text("call " + fflush_label)

    if arg[0]=='SHOW'or arg[0] == 'SHOWLN':
        if arg[0] == 'SHOWLN':
            print_stm(arg[1],arg[2],True,count)
        else:
            print_stm(arg[1],arg[2],False,count)



def assign_stm(dest, source):
    global global_var
    d_type = get_type(dest)
    s_type = get_type(source)
    if s_type == 'CONSTANT':
        add_text('mov rax, ' + str(source))
    elif s_type == 'ID':
        get_var(source)
        add_text('mov rax, [%s]' % source)
    elif s_type =="LEN":
        get_len(source[1])
    elif s_type == 'EXP':
        exp_main(source)
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


def plus_stm(a, b):
    a_type = get_type(a)
    b_type = get_type(b)
    if a_type == 'CONSTANT':
        add_text("mov rax, %s" % a)

    elif a_type == 'ID':
        get_var(a)
        add_text("mov rax, [%s]" % a)
    elif a_type == 'LEN':
        get_len(a[1])
    elif a_type == 'EXP':
        exp_main(a)
    elif a_type == 'ARRAY':
        index_type = get_type(a[2])
        if index_type == 'ID':
            get_var(a[2])
            add_text('mov rbx, %s' % a[1])
            add_text('mov rcx, [%s]' % a[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_text('mov rax, [rbx]')
        elif index_type == 'CONSTANT':
            get_arr(a[1], a[2])
            add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))
    else:
        error_token()

    if b_type == 'CONSTANT':
        add_text("add rax, %s" % b)
    elif b_type == 'ID':
        get_var(b)
        add_text("add rax, [%s]" % b)
    elif b_type == 'LEN':
        add_text("push rax")
        get_len(b[1])
        add_text("pop rbx")
        add_text("add rax,rbx")
    elif b_type == 'EXP':
        add_text("push rax")
        exp_main(b)
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

def minus_stm(a, b):
    global asmtext
    a_type = get_type(a)
    b_type = get_type(b)
    if a_type == 'CONSTANT':
        add_text("mov rax, %s" % a)
    elif a_type == 'ID':
        get_var(a)
        add_text("mov rax, [%s]" % a)
    elif a_type == 'LEN':
        get_len(a[1])
    elif a_type == 'EXP':
        exp_main(a)
    elif a_type == 'ARRAY':
        index_type = get_type(a[2])
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

    if b_type == 'CONSTANT':
        add_text("sub rax, %s" % b)
    elif b_type == 'ID':
        get_var(b)
        add_text("sub rax, [%s]" % b)
    elif b_type == 'LEN':
        add_text("push rax")
        get_len(b[1])
        add_text("mov rbx,rax")
        add_text("pop rax")
        add_text("sub rax,rbx")
    elif b_type == 'EXP':
        add_text("push rax")
        exp_main(b)
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


def multiply_stm(a, b):
    a_type = get_type(a)
    b_type = get_type(b)
    if a_type == 'CONSTANT':
         add_text("mov rax, %s" % a)
    elif a_type == 'ID':
        get_var(a)
        add_text("mov rax, [%s]" % a)
    elif a_type == 'LEN':
        get_len(a[1])
    elif a_type == 'EXP':
        exp_main(a)
    elif a_type == 'ARRAY':
        index_type = get_type(a[2])
        if index_type == 'ID':
            get_var(a[2])
            add_text('mov rbx, %s' % a[1])
            add_text('mov rcx, [%s]' % a[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_text('mov rax, [rbx]')
        elif index_type == 'CONSTANT':
            get_arr(a[1], a[2])
            add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))
    else:
        error_token()

    if b_type == 'CONSTANT':
        add_text("imul rax, %s" % b)
    elif b_type == 'ID':
        get_var(b)
        add_text("imul rax, [%s]" % b)
    elif b_type == 'LEN':
        add_text("push rax")
        get_len(b[1])
        add_text("pop rbx")
        add_text('imul rax, rbx')
    elif b_type == 'EXP':
        add_text("push rax")
        exp_main(b)
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


def divide_stm(a, b):
    a_type = get_type(a)
    b_type = get_type(b)
    add_text('xor rdx, rdx')
    if a_type == 'CONSTANT':
        add_text("mov rax,  %s" % a)
    elif a_type == 'ID':
        get_var(a)
        add_text('mov rax, [%s]' % a)
    elif a_type == 'LEN':
        get_len(a[1])
    elif a_type == 'EXP':
        exp_main(a)
    elif a_type == 'ARRAY':
        index_type = get_type(a[2])
        if index_type == 'ID':
            get_var(a[2])
            add_text('mov rbx, %s' % a[1])
            add_text('mov rcx, [%s]' % a[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_text('mov rax, [rbx]')

        elif index_type == 'CONSTANT':
            get_arr(a[1], a[2])
            add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))


    else:
        error_token()

    add_text('cqo')
    # add_text('xor rdx, rdx')
    if b_type == 'CONSTANT':
        if b == 0 :
            print_error("division by zero is undefined")
        add_text('mov rcx, %s' % b)
        add_text('idiv rcx')
    elif b_type == 'ID':
        get_var(b)
        add_text('mov rcx, [%s]' % b)
        add_text('idiv rcx')
    elif b_type == 'LEN':
        add_text("push rax")
        get_len(b[1])
        add_text("mov rcx, rax")
        add_text("pop rbx")
        add_text('cqo')
        add_text("mov rax, rbx")
        add_text('idiv rcx')
    elif b_type == 'EXP':
        add_text("push rax")
        exp_main(b)
        add_text("mov rcx, rax")
        add_text("pop rbx")
        add_text('cqo')
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
            add_text('cqo')
            add_text('idiv rcx')
        elif index_type == 'CONSTANT':
            get_arr(b[1], b[2])
            add_text('mov rcx, [%s + %s * 8]' % (b[1], b[2]))
            add_text('cqo')
            add_text('idiv rcx')
    else:
        error_token()


def mod_stm(a, b):
    a_type = get_type(a)
    b_type = get_type(b)
    add_text('xor rdx, rdx')
    if a_type == 'CONSTANT':
        add_text("mov rax,  %s" % a)
    elif a_type == 'ID':
        get_var(a)
        add_text('mov rax, [%s]' % a)
    elif a_type == 'LEN':
        get_len(a[1])
    elif a_type == 'EXP':
        exp_main(a)
    elif a_type == 'ARRAY':
        index_type = get_type(a[2])
        if index_type == 'ID':
            get_var(a[2])
            add_text('mov rbx, %s' % a[1])
            add_text('mov rcx, [%s]' % a[2])
            add_text('imul rcx, 8')
            add_text('add rbx, rcx')
            add_text('mov rax, [rbx]')
        elif index_type == 'CONSTANT':
            get_arr(a[1], a[2])
            add_text('mov rax, [%s + %s * 8]' % (a[1], a[2]))
    else:
        error_token()

    add_text('cqo')
    if b_type == 'CONSTANT':
        if b == 0 :
            print_error("division by zero is undefined")
        add_text('mov rcx, %s' % b)
        add_text('idiv rcx')
        add_text('mov rax, rdx')
    elif b_type == 'ID':
        get_var(b)
        add_text('mov rcx, [%s]' % b)
        add_text('idiv rcx')
        add_text('mov rax, rdx')
    elif b_type == 'LEN':
        add_text("push rax")
        get_len(b[1])
        add_text("mov rcx, rax")
        add_text("pop rbx")
        add_text("mov rax, rbx")
        add_text('cqo')
        add_text('idiv rcx')
        add_text("mov rax, rdx")
    elif b_type == 'EXP':
        add_text("push rax")
        exp_main(b)
        add_text("mov rcx, rax")
        add_text("pop rbx")
        add_text('cqo')
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
            add_text('cqo')
            add_text('idiv rcx')
            add_text('mov rax, rdx')
        elif index_type == 'CONSTANT':
            get_arr(b[1], b[2])
            add_text('mov rcx, [%s + %s * 8]' % (b[1], b[2]))
            add_text('cqo')
            add_text('idiv rcx')
            add_text('mov rax, rdx')
    else:
        error_token()





def less_equ_stm():
    add_text("jg _EXIF%d" % global_if_counter)


def greater_equ_stm():
    add_text("jl _EXIF%d" % global_if_counter)


def less_stm():
    add_text("jge _EXIF%d" % global_if_counter)


def greater_stm():
    add_text("jle _EXIF%d" % global_if_counter)


def not_equal_stm():
    add_text("je _EXIF%d" % global_if_counter)


def equal_stm():
    add_text("jne _EXIF%d" % global_if_counter)
