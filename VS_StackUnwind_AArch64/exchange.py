from elftools.elf.elffile import ELFFile
from elftools.dwarf.callframe import ZERO
from elftools.dwarf.callframe import RegisterRule
from elftools.dwarf.callframe import CFARule
from elftools.dwarf.callframe import ZERO
from elftools.elf.elffile import ELFFile

def set_register(return_row, table, row_pc):
    if table[row_pc]["LR"] != None:
        reg_data = RegisterRule(RegisterRule.OFFSET, table[row_pc]["LR"])
        return_row[30] = reg_data
    if table[row_pc]["FP"] != None:
        reg_data = RegisterRule(RegisterRule.OFFSET, table[row_pc]["FP"])
        return_row[29] = reg_data
    if table[row_pc]["X19"] != None:
        reg_data = RegisterRule(RegisterRule.OFFSET, table[row_pc]["X19"])
        return_row[19] = reg_data
    if table[row_pc]["X20"] != None:
        reg_data = RegisterRule(RegisterRule.OFFSET, table[row_pc]["X20"])
        return_row[20] = reg_data
    if table[row_pc]["X21"] != None:
        reg_data = RegisterRule(RegisterRule.OFFSET, table[row_pc]["X21"])
        return_row[21] = reg_data
    if table[row_pc]["X22"] != None:
        reg_data = RegisterRule(RegisterRule.OFFSET, table[row_pc]["X22"])
        return_row[22] = reg_data
    if table[row_pc]["X23"] != None:
        reg_data = RegisterRule(RegisterRule.OFFSET, table[row_pc]["X23"])
        return_row[23] = reg_data
    if table[row_pc]["X24"] != None:
        reg_data = RegisterRule(RegisterRule.OFFSET, table[row_pc]["X24"])
        return_row[24] = reg_data
    if table[row_pc]["X25"] != None:
        reg_data = RegisterRule(RegisterRule.OFFSET, table[row_pc]["X25"])
        return_row[25] = reg_data
    if table[row_pc]["X26"] != None:
        reg_data = RegisterRule(RegisterRule.OFFSET, table[row_pc]["X26"])
        return_row[26] = reg_data
    if table[row_pc]["X27"] != None:
        reg_data = RegisterRule(RegisterRule.OFFSET, table[row_pc]["X27"])
        return_row[27] = reg_data
    if table[row_pc]["X28"] != None:
        reg_data = RegisterRule(RegisterRule.OFFSET, table[row_pc]["X28"])
        return_row[28] = reg_data
    
    return return_row

def set_CFA(table, row_pc):
    cfa_data = CFARule()
    if table[row_pc]['base'] == 'SP':
        base = 31
    elif table[row_pc]['base'] == 'FP':
        base = 29
    else:
        print('error: exchange.py setCFA')
        exit()
    cfa_data = CFARule(base, table[row_pc]['CFA'], None)
    return cfa_data

def exchange_table(eh_frame_list):
    eh_frame = []
    for table in eh_frame_list:
        return_table = []

        for row_pc in table:
            return_row = {}
            return_row['pc'] = int(row_pc, 0)
            return_row['cfa'] = set_CFA(table, row_pc)
            return_row = set_register(return_row, table, row_pc)
            return_table.append(return_row)

        eh_frame.append(return_table)
    return eh_frame
