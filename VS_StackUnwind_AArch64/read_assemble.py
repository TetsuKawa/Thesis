import sys
from elftools.elf.elffile import ELFFile
from capstone import *
import re

#get opperand
def process_file(filename):
    print('Processing file:', filename)
    with open(filename, 'rb') as f:
        elf = ELFFile(f)
        code = elf.get_section_by_name('.text')
        ops = code.data()
        addr = code['sh_addr']
        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        callee_list = {'x19': 'X19', 'x20': 'X20', 'x21': 'X21', 'x22': 'X22', 'x23': 'X23', 'x24': 'X24', 'x25': 'X25', 'x26': 'X26', 'x27': 'X27', 'x28': 'X28', 'x29': 'FP', 'x30': 'LR'}
        dict = {}
        for i in md.disasm(ops, addr):
            if i.mnemonic == 'stp':
                ope = i.op_str.split('[')
                ope_regs_list = re.split('[ ,\t]', ope[0])
                ope_regs = [a for a in ope_regs_list if a != '']
                if ope[1][-1] == ']':
                    ope_offset_list = re.split('[ ,\]\t#]', ope[1])
                    ope_offset = [a for a in ope_offset_list if a != '']
                    if ope_regs[0] in callee_list or ope_regs[1] in callee_list:
                        dict[i.address] = {'instr': i.mnemonic, 'regs': [callee_list[ope_regs[0]],callee_list[ope_regs[1]]] , 'offset': ope_offset}
            elif i.mnemonic == 'str':
                ope = i.op_str.split('[')
                ope_regs_list = re.split('[ ,\t]', ope[0])
                ope_regs = [a for a in ope_regs_list if a != '']
                if ope[1][-1] == '!':
                    ope_offset_list = re.split('[ \],\t#!]', ope[1])
                    ope_offset = [a for a in ope_offset_list if a != '']
                    if ope_regs[0] in callee_list:
                        dict[i.address] = {'instr': i.mnemonic, 'regs': [callee_list[ope_regs[0]]], 'offset': ope_offset}
            elif i.mnemonic == 'ldr':
                ope = i.op_str.split('[')
                ope_regs_list = re.split('[ ,\t]', ope[0])
                ope_regs = [a for a in ope_regs_list if a != '']
                if '],' in ope[1]:
                    ope_offset_list = re.split('[ \],\t#!]', ope[1])
                    ope_offset = [a for a in ope_offset_list if a != '']
                    if ope_regs[0] in callee_list:
                        dict[i.address] = {'instr': i.mnemonic, 'regs': [callee_list[ope_regs[0]]], 'offset': ope_offset}
        print(dict)
        return dict



if __name__ == '__main__':
    if sys.argv[1] == '--test':
        for filename in sys.argv[2:]:
            instr_dict = process_file(filename)