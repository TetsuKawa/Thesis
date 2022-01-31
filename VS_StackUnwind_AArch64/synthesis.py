# from fnmatch import fnmatchcase
import bap
import read_assemble as ra
import sys
from exchange import exchange_table

#process next blk
def direct_case(targets, last_pc, tmp_row, tmp_pc, mode, spe_list, flg, pre_tmp, success):
    tid = targets.arg
    print(tid)
    print(type(tid))
    jmp_pc = tid.name
    if jmp_pc[0] != '%':
        return  True
    next_blk = blks.find(tid)            
    if next_blk != None:
        success = cfg(next_blk, last_pc, tmp_row, tmp_pc, mode, spe_list, flg, pre_tmp, success)
        if not success:
            return False
    return True

#decode next blk
def next_block(blk_jmps, last_pc, tmp_row, tmp_pc, mode, spe_list, flg, pre_tmp, success):
    global eh_frame

    for j in range(len(blk_jmps)):
        targets = blk_jmps[j].target
        print()
        print(targets)
        print('------------------------------------------------------------------------------------------------')
        if type(targets) is bap.bir.Direct:
            success = direct_case(targets, last_pc, tmp_row, tmp_pc, mode, spe_list, flg, pre_tmp, success)
            if not success:
                return success
        elif type(targets) is tuple:
            for k in range(len(targets)):
                tar = targets[k]
                if type(tar) is bap.bir.Direct:
                    success = direct_case(tar, last_pc, tmp_row, tmp_pc, mode, spe_list, flg, pre_tmp, success)
                    if not success:
                        return success
                elif type(tar) is bap.bir.Indirect:
                    if any(spe_list):
                        print(spe_list)
                        for row_address in spe_list:
                            if row_address > int(tmp_pc, 0):
                                tmp_row = insert_row(row_address, row_address + 4, tmp_row)
                                last_pc = str(hex(int(tmp_pc,0) + 4))
                                spe_list.remove(row_address)
                                tmp_pc = last_pc
                    elif tar.arg.name == 'LR':
                        eh_frame[str(hex(int(tmp_pc,0) + 4))] = tmp_row
                else:
                    print('No type1')
                    print(type(tar))
                    exit()
        elif type(targets) is bap.bir.Indirect:
            if any(spe_list):
                for row_address in spe_list:
                    if row_address > int(tmp_pc, 0):
                        tmp_row = insert_row(row_address, row_address + 4, tmp_row)
                        last_pc = str(hex(int(tmp_pc,0) + 4))
                        spe_list.remove(row_address)
                        tmp_pc = last_pc
            elif tar.arg.name == 'LR':
                eh_frame[str(hex(int(tmp_pc,0) + 4))] = tmp_row
        else:
            print('No type2')
            print(type(targets))
            exit()
    return True

#make up a lost instr
def insert_row(row_address, tmp_row):
    global eh_frame
    global instr_dict
    row = instr_dict[row_address]
    regs = row['regs']
    instr = row['instr']
    ope_list = row['offset']
    index = ope_list[0]

    if index != 'sp':
        print('index error in insert_row')
        exit()
    if len(ope_list) == 2:
        offset = str(ope_list[1])
        offset = form_offset(int(offset, 0))
    elif len(ope_list) == 1:
        offset = 0
    if instr == 'stp':
        tmp_row = set_row(offset - tmp_row['CFA'], regs[0], tmp_row)
        tmp_row = set_row(offset - tmp_row['CFA'] + 8, regs[1], tmp_row)
    elif instr == 'str':
        tmp_row = set_row(tmp_row['CFA'] - offset, 'CFA', tmp_row)
        tmp_row = set_row(-tmp_row['CFA'], regs[0], tmp_row)
    elif instr == 'ldr':
        tmp_row = set_row(None, regs[0], tmp_row)
        tmp_row = set_row(tmp_row['CFA'] - offset, 'CFA', tmp_row)
    return tmp_row
    

#set row information
def set_row(offset, reg, tmp_row):
    if reg == 'LR':
        return {"base": tmp_row["base"], "CFA": tmp_row["CFA"], "LR": offset, "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
    elif reg == 'FP':
        return {"base": tmp_row["base"], "CFA": tmp_row["CFA"], "LR": tmp_row["LR"], "FP": offset, "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
    elif reg == "X19":
        return {"base": tmp_row["base"], "CFA": tmp_row["CFA"], "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": offset, "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
    elif reg == "X20":
        return {"base": tmp_row["base"], "CFA": tmp_row["CFA"], "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": offset, "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
    elif reg == "X21":
        return {"base": tmp_row["base"], "CFA": tmp_row["CFA"], "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": offset, "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}    
    elif reg == "X22":
        return {"base": tmp_row["base"], "CFA": tmp_row["CFA"], "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": offset, "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
    elif reg == "X23":
        return {"base": tmp_row["base"], "CFA": tmp_row["CFA"], "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": offset, "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
    elif reg == "X24":
        return {"base": tmp_row["base"], "CFA": tmp_row["CFA"], "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": offset, "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
    elif reg == "X25":
        return {"base": tmp_row["base"], "CFA": tmp_row["CFA"], "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": offset, "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
    elif reg == "X26":
        return {"base": tmp_row["base"], "CFA": tmp_row["CFA"], "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": offset, "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
    elif reg == "X27":
        return {"base": tmp_row["base"], "CFA": tmp_row["CFA"], "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": offset, "X28": tmp_row["X28"]}
    elif reg == "X28":
        return {"base": tmp_row["base"], "CFA": tmp_row["CFA"], "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": offset}
    elif reg == "CFA":
        return {"base": tmp_row["base"], "CFA": offset, "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
    elif reg == "base":
        return {"base": offset, "CFA": tmp_row["CFA"], "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
    else:
        print('set_row error')
        exit()

#form offset
def form_offset(value):
    if value >> 63 == 1:
        value -= 1
        value = value ^ mask
        value = -1 * value
    return value

#check a merge point
def merge_check(top_pc, pre_tmp):
    global eh_frame
    global first_pc

    top_pc = int(top_pc, 0)
    current_row_pc = int(first_pc, 0)
    for pc in eh_frame:
        pc = int(pc, 0)
        if top_pc > pc and current_row_pc < pc:
            current_row_pc = pc
    
    if eh_frame[str(hex(current_row_pc))] == pre_tmp:
        return True
    else:
        print('mergeError')
        print(eh_frame)
        print(str(hex(current_row_pc)))
        print(pre_tmp)
        exit()

#synthesis stack unwinding information
def cfg(current_blk, last_pc, tmp_row, tmp_pc, mode, spe_list, flg, pre_tmp, success):
    global eh_frame
    global already
    global tmp_sp_cfa
    global blkname
    current_tid = current_blk.arg[0]

    print('current:')
    print(current_tid)

    #check merge point
    if current_tid in already:
        print('already block')
        return  merge_check(str(hex(int(current_blk.arg[1].arg[0][0].arg[1], 0))), pre_tmp)

    else:
        already.append(current_tid)
        current_blk_defs = current_blk.defs
        print('++++++++++++++++++++++++++++++++++++++++++++++++++')
        
        #synthsis a unwinding row
        for i in current_blk_defs: 
            attrs = i.attrs.arg[0]
            if attrs[0].arg[0] == 'address':
                address = attrs[0].arg[1]
                address = str(hex(int(address,0)))
            else:
                print('error: add_row address error')
                exit()

            if tmp_pc != None and tmp_pc != address:
                del_list = []
                for row_address in spe_list:
                    if int(tmp_pc, 0) < row_address and row_address < int(address, 0):
                        if eh_frame[last_pc] != tmp_row:
                            eh_frame[str(hex(row_address))] = tmp_row
                            pre_tmp = tmp_row
                            last_pc = str(hex(row_address))
                            print('a')
                            print(str(hex(row_address)))
                        else:
                            print('same last row')
                            print()
                        tmp_row = insert_row(row_address, tmp_row)
                        del_list.append(row_address)
                    else:
                        if eh_frame[last_pc] != tmp_row:
                            eh_frame[address] = tmp_row
                            pre_tmp = tmp_row
                            last_pc = address
                        else:
                            print('same last row')
                            print()

                if eh_frame[last_pc] != tmp_row:
                    eh_frame[address] = tmp_row
                    pre_tmp = tmp_row
                    last_pc = address
                    print('same last row')
                    print()
                
                for del_pc in del_list:
                    if del_pc in spe_list:
                        spe_list.remove(del_pc)

                tmp_pc = address

            print()
            print(i)
            print(tmp_sp_cfa)
            print('===================================')
            target = i.arg[2].name
            value = i.arg[3]
            culc_type = type(value)

            
            if mode == 'x29-mode' and target == 'FP':
                #base-register  sp >>>> fp
                if flg == 0:
                    if culc_type == bap.bil.Var and value.name == 'SP':
                        flg = 1
                        tmp_sp_cfa = tmp_row["CFA"]
                        tmp_row = set_row('FP', "base", tmp_row)
                        tmp_row = set_row(-tmp_row["FP"], "CFA", tmp_row)
                    elif culc_type == bap.bil.PLUS:
                        value_0 = value.arg[0]
                        value_1 = value.arg[1]
                        print(value_0)
                        print(value_1)
                        if value_0.name == 'SP' and type(value_1) == bap.bil.Int:
                            tmp_sp_cfa = tmp_row["CFA"]
                            tmp_row = set_row('FP', "base", tmp_row)
                            tmp_row = set_row(-tmp_row["FP"], "CFA", tmp_row)
                            flg = 1
                    elif culc_type == bap.bil.MINUS:
                        value_0 = value.arg[0]
                        value_1 = value.arg[1]
                        print(value_0)
                        print(value_1)
                        if value_0.name == 'SP' and type(value_1) == bap.bil.Int:
                            tmp_sp_cfa = tmp_row["CFA"]
                            tmp_row = set_row('FP', "base", tmp_row)
                            tmp_row = set_row(-tmp_row["FP"], "CFA", tmp_row)
                            flg = 1

                #base-register  fp >>>> sp
                else:
                    tmp_row = set_row('SP', "base", tmp_row)
                    tmp_row = set_row(tmp_sp_cfa, "CFA", tmp_row)
                    flg = 0
                
            #renew row by store instr
            if target == 'mem' and culc_type == bap.bil.Store:
                objct = value.arg[2]
                if type(objct) == bap.bil.Var:
                    reg = objct.name
                    if reg in tmp_row:
                        value_under = value.arg[1]
                        store_culc_type = type(value_under)
                        if store_culc_type == bap.bil.PLUS:
                            value_under_0 = value_under.arg[0]
                            value_under_1 = value_under.arg[1]
                            if value_under_0.name == 'SP' and type(value_under_1) == bap.bil.Int:
                                if flg == 0:
                                    offset = form_offset(value_under_1.value) - tmp_row["CFA"]
                                    tmp_row = set_row(offset, reg, tmp_row)
                                else:
                                    offset = form_offset(value_under_1.value) - tmp_sp_cfa
                                    tmp_row = set_row(offset, reg, tmp_row)
                            elif value_under_0.name == 'FP' and type(value_under_1) == bap.bil.Int:
                                offset = form_offset(value_under_1.value) - tmp_row["CFA"]
                                tmp_row = set_row(offset, reg, tmp_row)
                        else:
                            print('set regs error')
                            print(store_culc_type)
                            exit()
            
            #renew row by load instr
            if target in tmp_row and culc_type == bap.bil.Load:
                tmp_row = set_row(None, target, tmp_row)
            
            #renew row by sp or lost trace
            if target == 'SP' and flg == 0:
                if culc_type == bap.bil.PLUS:
                    print(culc_type)
                    value_0 = value.arg[0]
                    value_1 = value.arg[1]
                    print(value_0)
                    print(value_1)
                    if value_0.name == 'SP' and type(value_1) == bap.bil.Int:
                        tmp_row = {"base": tmp_row["base"], "CFA": tmp_row["CFA"] - form_offset(value_1.value), "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
                    else:
                        print()
                        print('sp-mode >>>>>>>>>>>>> x29-mode')
                        print()
                        return False

                elif culc_type == bap.bil.MINUS:
                    print(culc_type)
                    value_0 = value.arg[0]
                    value_1 = value.arg[1]
                    print(value_0)
                    print(value_1)
                    if value_0.name == 'SP' and type(value_1) == bap.bil.Int:
                        tmp_row = {"base": tmp_row["base"], "CFA": tmp_row["CFA"] + form_offset(value_1.value), "LR": tmp_row["LR"], "FP": tmp_row["FP"], "X19": tmp_row["X19"], "X20": tmp_row["X20"], "X21": tmp_row["X21"], "X22": tmp_row["X22"], "X23": tmp_row["X23"], "X24": tmp_row["X24"], "X25": tmp_row["X25"], "X26": tmp_row["X26"], "X27": tmp_row["X27"], "X28": tmp_row["X28"]}
                    else:
                        print()
                        print('sp-mode >>>>>>>>>>>>> x29-mode')
                        print()
                        return False
 
                else:
                    print('error: culc_type')
                    print(culc_type)
                    print()
                    print('sp-mode >>>>>>>>>>>>> x29-mode')
                    return False
                    
        print('++++++++++++++++++++++++++++++++++++++++++++++++++')
  
        blk_jmps = current_blk.jmps
        success = next_block(blk_jmps, last_pc, tmp_row, tmp_pc, mode, spe_list, flg, pre_tmp, success)
        return success



mask = 0xffffffffffffffff
tmp_list =[]
tmp_sp_cfa = 0
already =[]
eh_frame = {}
blks = []
first_pc = None
instr_dict =[]
eh_frame_list = []

#initial process and try two modes
def synmain(filename):
    global tmp_list
    global tmp_sp_cfa
    global already
    global eh_frame
    global blks
    global first_pc
    global instr_dict
    global eh_frame_list

    print(filename)
    proj = bap.run(filename)
    instr_dict = ra.process_file(filename)
    prog_list = proj.program.subs.arg[0]
    fde_top_dict = {}
    spe_fde_top_dict = {}


    for i in range(len(prog_list)):
        fde_top_dict[int(prog_list[i].arg[1].arg[0][0].arg[1], 0)] = prog_list[i].arg[0].arg[1]
    print()
    print(fde_top_dict)
    print()
    for spe_id in instr_dict:
        tmp_id = None
        tmp_list = []
        for top_id in fde_top_dict:
            if top_id <= spe_id:
                if tmp_id == None:
                    tmp_id = top_id
                elif tmp_id < top_id:
                    tmp_id = top_id
        if not (fde_top_dict[tmp_id] in spe_fde_top_dict):
            spe_fde_top_dict[fde_top_dict[tmp_id]] = [spe_id]
        else:
            spe_fde_top_dict[fde_top_dict[tmp_id]].append(spe_id)

    print(spe_fde_top_dict)

    for i in fde_top_dict.values():
        fn = proj.program.subs.find(i)
        print(i)
        if fn != None:
            blks = fn.blks
        else:
            print('blocks error')
            exit()

        #try sp-index-mode

        first_pc = fn.arg[1].arg[0][0].arg[1]
        first_pc = str(hex(int(first_pc,0)))
        already = []
        eh_frame = {}
        last_pc = first_pc
        tmp_row = {"base" : 'SP',"CFA": 0, "LR": None, "FP": None, "X19": None, "X20": None, "X21": None, "X22": None, "X23": None, "X24": None, "X25": None, "X26": None, "X27": None, "X28": None} #[cfa (offset from rsp), x30 (offset from cfa), x29 (offset from cfa)]
        tmp_pc = first_pc
        success = True
        flg = 0
        eh_frame[first_pc] = tmp_row
        pre_tmp = tmp_row
        tmp_sp_cfa = 0
        if i in spe_fde_top_dict:
            spe_list = spe_fde_top_dict[i][:]
        else:
            spe_list = []

        success = cfg(blks[0], last_pc, tmp_row, tmp_pc, 'sp-mode', spe_list, flg, pre_tmp, success)
        
        if success:
            eh_frame_list.append(eh_frame)
            print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||')
        else:
            
            #try x29-index-mode

            success = True
            flg = 0
            already = []
            eh_frame = {}
            last_pc = first_pc
            tmp_row = {"base": 'SP',"CFA": 0, "LR": None, "FP": None, "X19": None, "X20": None, "X21": None, "X22": None, "X23": None, "X24": None, "X25": None, "X26": None, "X27": None, "X28": None} #[cfa (offset from rsp), x30 (offset from cfa), x29 (offset from cfa)]
            tmp_pc = first_pc
            eh_frame[first_pc] = tmp_row
            pre_tmp = tmp_row
            tmp_sp_cfa = 0
            if i in spe_fde_top_dict:
                spe_list = spe_fde_top_dict[i][:]
            else:
                spe_list = []
            
            success = cfg(blks[0], last_pc, tmp_row, tmp_pc, 'x29-mode', spe_list, flg, pre_tmp, success)
            
            if success:
                eh_frame_list.append(eh_frame)
                print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||')
            else:
                print('error: both of 2 mode')
                exit()

    #form stack unwinding information
    eh_frame_list = exchange_table(eh_frame_list)
    return eh_frame_list

if __name__ == '__main__':
    filename = sys.argv[1]
    eh_frame_list = synmain(filename)
    print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||')
    print(eh_frame_list)