import parse2
import tt
import platform

tt.statement_main(parse2.getTree())
file = open("test.asm", 'w')
file.writelines(tt.asmheader)
file.writelines(tt.asmdata)
file.writelines(tt.asmtext)
file.writelines(tt.asmleave)
file.close()
# print(parse2.getTree())
