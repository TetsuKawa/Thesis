import re
import sys
sys.path.append('/home/tetsu/Desktop/stackUnwind')
import synthesis
from elftools.elf.elffile import ELFFile
from elftools.dwarf.callframe import ZERO
import gdb

#input dwarf info
def process_file(filename):
    print('Processing file:', filename)
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)

        if not elffile.has_dwarf_info():
            print('  file has no DWARF info')
            return

        dwarfinfo = elffile.get_dwarf_info()
        fdes = dwarfinfo.EH_CFI_entries()
        
    return fdes

#decode table
def get_decode_table(frame_table):
    decode = frame_table.get_decoded()
    return decode.table

#get the top address list of fdes 
def make_pc_list(eh_frame):
    global mode

    pc_list = []
    if mode == 'syn':
        for table in eh_frame:
            table_init = table[0]
            pc_list.append(table_init['pc'])
    else:
        for frame_table in eh_frame:
            if type(frame_table) != ZERO:
                table = get_decode_table(frame_table)
                table_init = table[0]
                pc_list.append(table_init['pc'])
    return pc_list

#get the num of fde included pc
def check_pc_block(pc_list, pc):
    tmp_num = 0
    for num in range(len(pc_list)):
        if pc_list[num] <= pc:
            if pc_list[tmp_num] < pc_list[num]:
                tmp_num = num         
    return tmp_num

#get an offset information of pc && reg
def get_offset(frame_table, pc, reg):
    global mode
    reg = int(reg)

    if mode == 'syn':
        table = frame_table
    else:
        if type(frame_table) != ZERO:
            table = get_decode_table(frame_table)
        else:
            print('error: get_offset ZERO')

    for dic in table:
        if dic['pc'] <= pc:
            state_dic = dic
        else:
            break

    if state_dic.get('cfa') and state_dic.get(reg):
        return state_dic['cfa'].offset, state_dic['cfa'].reg, state_dic[reg].arg

    return None, None, None

#get current regs information
def get_info():
    regs = gdb.execute('i r', to_string=True)
    regs_list = regs.split('\n')
    info = {}
    for i in range(len(regs_list)-1):
        line = regs_list[i].split()
        info[line[0]] = line[1]
    return info

#get current instr information
def get_next_instr():
    assemble = gdb.execute('x/1i $pc',to_string = True)
    assemble_list = assemble.split(':')
    assemble_pcside = assemble_list[0].split()
    assemble_instrside = assemble_list[1].split('[')
    assemble_instr_operand = re.split('[ \],\t#!\n]', assemble_instrside[0])
    instr = [a for a in assemble_instr_operand if a != '']
    pc = assemble_pcside[1]
    assemble_list = re.split(':\n\t',assemble)
    print('===========================================')
    print(assemble_list)
    print('===========================================')
    return pc,instr

#form an address
def attach_mask(addr):
    mask = "0xaaaaaaaa0000"
    mask = int(mask,0)
    addr = int(addr,0)
    addr = addr - mask
    return addr
    
#from contents
def get_contents(content):
    content_list = content.split()
    addr = '0x'
    for i in content_list[8:0:-1]:
        addr = addr + i[2:4]
    return addr

#check loaded regs
def check_dict(row, info, current_load_regs):
    fault_regs = []
    for reg in current_load_regs:
        if row[reg] != info[reg]:
            fault_regs.append(reg)
    if any(fault_regs):
        return fault_regs
    else:
        return True

#get operands
def get_operand(instr_list):
    ope = []
    if instr_list[0] == 'str':
        ope.append(instr_list[1])
    elif instr_list[0] == 'stp':
        ope.append(instr_list[1])
        ope.append(instr_list[2])
    else:
        print('error: getOperand')
        exit()
    return ope

#check error_regs
def check_error(error):
    for reg in error:
        if error[reg] != None:
            return True
    return False




mode = 'val' #or syn < validate a synthesis stack unwinding information
filename = 'test'
gdb.execute('set pagination off')

if mode == 'syn':
    eh_frame = synthesis.synmain(filename)
else:
    eh_frame = process_file(filename)

abstract_state = []
pc_list = make_pc_list(eh_frame)
print(pc_list)
gdb.execute('file ' + filename)
gdb.execute('start')
pc, instr = get_next_instr()
info = get_info()
mpc = attach_mask(pc)
list_num = check_pc_block(pc_list, mpc)
check_frag = False
error_regs = {'x30': None, 'x29': None, 'x19': None, 'x20': None, 'x21': None, 'x22': None, 'x23': None, 'x24': None, 'x25': None, 'x26': None, 'x27': None, 'x28': None}
regs_info = {'x30': info['x30'], 'x29': info['x29'], 'x19': info['x19'], 'x20': info['x20'], 'x21': info['x21'], 'x22': info['x22'], 'x23': info['x23'], 'x24': info['x24'], 'x25': info['x25'], 'x26': info['x26'], 'x27': info['x27'], 'x28': info['x28']}
store_regs = []
current_store_regs = []
load_regs = []

#initial_process
for reg in regs_info:
    cfa_offset,  index_reg, reg_offset = get_offset(eh_frame[list_num], mpc, reg[1::])
    if cfa_offset != None and reg_offset != None:
        if index_reg == 31:
            index = int(info['sp'], 0)
        elif index_reg == 29:
            index = int(info['x29'], 0)
        else:
            print('error reg')
            print(reg)
            exit()
        reg_address = index + cfa_offset + reg_offset
        reg_address = hex(reg_address)
        reg_address_info_pre = gdb.execute('x/8xb '+ reg_address ,to_string=True)
        reg_address_info = get_contents(reg_address_info_pre)
        regs_info[reg] = reg_address_info
        current_store_regs.append(reg)
abstract_state.append(regs_info)
store_regs.append(current_store_regs)
current_store_regs = []
pre_pc, pre_instr = pc, instr
gdb.execute('stepi')

while True:
    pc, instr = get_next_instr()
    info = get_info()
    regs_info = {'x30': info['x30'], 'x29': info['x29'], 'x19': info['x19'], 'x20': info['x20'], 'x21': info['x21'], 'x22': info['x22'], 'x23': info['x23'], 'x24': info['x24'], 'x25': info['x25'], 'x26': info['x26'], 'x27': info['x27'], 'x28': info['x28']}
    mpc = attach_mask(pc)
    list_num = check_pc_block(pc_list, mpc)
    print('abstract_state:')
    print(abstract_state)
    print()

    #all regs of regs_info.keys()
    for reg in regs_info:
        cfa_offset,  index_reg, reg_offset = get_offset(eh_frame[list_num], mpc, reg[1::])

        #if reg information exists in fde: 
        if cfa_offset != None and reg_offset != None:
            current_store_regs.append(reg)
            if index_reg == 31:
                index = int(info['sp'], 0)
            elif index_reg == 29:
                index = int(info['x29'], 0)
            else:
                print('error reg')
                print(reg)
                exit()
            reg_address = index + cfa_offset + reg_offset
            reg_address = hex(reg_address)
            reg_address_info_pre = gdb.execute('x/8xb '+ reg_address ,to_string=True)
            reg_address_info = get_contents(reg_address_info_pre)

            #fix error_regs
            if error_regs[reg] != None:
                error_regs[reg] = None

            if any(abstract_state):

                #validate real execution　and eh_frame information (function1)
                if int(reg_address_info, 0) != int(abstract_state[-1][reg],0):
                    print('error: comparison with a stack value > ' + reg)
                    print('real value: '+ reg_address_info)
                    print('eh_frame value: '+ abstract_state[-1][reg])
                    print(eh_frame[list_num].get_decoded())
                    exit()
                else:
                    print(reg + ' comparison with a stack value > OK')

        else:
            #push loaded regs 
            if reg in current_store_regs:
                load_regs.append(reg)
            
            #validate real execution　and eh_frame information (function2)
            if pre_instr[0] == 'str':
                pre_operand = get_operand(pre_instr)
                if reg in pre_operand:
                    error_regs[pre_operand[0]] = pre_pc
                    print('not enough information in eh_frame')
                    print(pre_pc,pre_instr)
                else:
                    print(reg + ' store command check > OK')

            elif pre_instr[0] == 'stp':
                pre_operand = get_operand(pre_instr)
                if reg in pre_operand:
                    error_regs[pre_operand[0]] = pre_pc
                    error_regs[pre_operand[1]] = pre_pc
                    print('not enough information in eh_frame')
                    print(pre_pc, pre_instr)
                else:
                    print(reg + ' store command check > OK')
            else:
                print(reg + ' need not to check')

    if instr[0] == 'bl':
        #check error_regs(function2)
        if check_error(error_regs):
            print('error: not enough information in eh_frame')
            print(error_regs)
        print('bl function')
        gdb.execute('stepi')
        info = get_info()
        abstract_state.append({'x30': info['x30'], 'x29': info['x29'], 'x19': info['x19'], 'x20': info['x20'], 'x21': info['x21'], 'x22': info['x22'], 'x23': info['x23'], 'x24': info['x24'], 'x25': info['x25'], 'x26': info['x26'], 'x27': info['x27'], 'x28': info['x28']})
        store_regs.append(current_store_regs)
        current_store_regs = []
    elif instr[0] == 'blr':
        #check error_regs(function2)
        if check_error(error_regs):
            print('error: not enough information in eh_frame')
            print(error_regs)
        print('bl function')
        gdb.execute('stepi')
        info = get_info()
        abstract_state.append({'x30': info['x30'], 'x29': info['x29'], 'x19': info['x19'], 'x20': info['x20'], 'x21': info['x21'], 'x22': info['x22'], 'x23': info['x23'], 'x24': info['x24'], 'x25': info['x25'], 'x26': info['x26'], 'x27': info['x27'], 'x28': info['x28']})
        store_regs.append(current_store_regs)
        current_store_regs = []
    elif instr[0] == 'ret':
        #check error_regs(function2)
        if check_error(error_regs):
            print('error: not enough information in eh_frame')
            print(error_regs)
        print('ret function')
        row = abstract_state.pop()

        #check loaded regs (function3)
        if check_dict(row, info, load_regs):
            print('Unwinging succesful')          
            if not abstract_state:
                print('All Unwinding Successful')
                break
            current_store_regs = store_regs[-1]
            load_regs = []
            gdb.execute('stepi')
            
        else:
            print('Unwinding False')
            print({'x30': info['x30'], 'x29': info['x29'], 'x19': info['x19'], 'x20': info['x20'], 'x21': info['x21'], 'x22': info['x22'], 'x23': info['x23'], 'x24': info['x24'], 'x25': info['x25'], 'x26': info['x26'], 'x27': info['x27'], 'x28': info['x28']})
            break
    else:
        gdb.execute('stepi')
    pre_pc, pre_instr = pc, instr
gdb.execute('q')
    