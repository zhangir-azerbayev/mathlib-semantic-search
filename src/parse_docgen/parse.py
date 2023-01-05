import json 
import ndjson
import sys
import re 
from tqdm import tqdm

PATH_DOCGEN_EXPORT = "docgen_export.json"
OUT_PATH = "docgen_export_with_formal_statement.jsonl"

def merge_typestars_of_binders(binders): 
    binders = [re.sub(r"Type u_[0-9]", "Type*", x) for x in binders]

    for i in range(len(binders)-1):
        if re.search(r"Type\*", binders[i]) and re.search(r"Type\*", binders[i+1]) and binders[i][0]==binders[i+1][0]:
            #print("left: ", binders[i][:binders[i].index(":")])
            #print("right: ", binders[i+1][1:])
            binders[i+1] = binders[i][:binders[i].index(":")] + binders[i+1][1:]
            binders[i] = ""

    return [x for x in binders if x != ""]
            
def assemble_statement(kind, nm, binders, tp): 
    binders = merge_typestars_of_binders(binders)

    statement = kind + " " + nm 
    for binder in binders: 
        sc = statement + " " + binder
        if len(sc[sc.rfind("\n")+1:]) > 80:
            statement += "\n\t" + binder
        else: 
            statement += " " + binder

    statement += " :\n\t" + tp

    return statement

def process_ue_string(arg: str): 
    #print(arg)
    arg = arg.replace("\n", " ")
    #print("ARG BEFORE PROCESSING: ", repr(arg))
    arg = re.sub(r"\ue000(.*?)\ue001", "", arg)
    arg = re.sub(r"\ue002", "", arg)
    #print("ARG: ", repr(arg))
    return arg

def parse_single_arg(arg): 
    if arg == "c": 
        return ""
    elif isinstance(arg, str): 
        return process_ue_string(arg)
    else: 
        assert isinstance(arg, list) 
        if arg[0] == "n":
            return parse_single_arg(arg[1:])
        else: 
            return "".join([parse_single_arg(x) for x in arg])


def main(): 
    print("loading docgen export...")
    with open(PATH_DOCGEN_EXPORT) as f:
        db = json.load(f)

    log = []

    for x in tqdm(db["decls"]): 
        # not memory efficient but that's ok
        if x["kind"]=="theorem": 

            list_of_args = [y["arg"] for y in x["args"]]
            binders = [parse_single_arg(y) for y in list_of_args]
            processed_tp = parse_single_arg(x["type"])

            statement = assemble_statement(x["kind"], x["name"], binders, processed_tp)

            # print(statement + "\n")

            log.append({
                **x, 
                "formal_statement": statement,
            })

    with open(OUT_PATH, "w") as f:
        ndjson.dump(log, f)

if __name__=="__main__": 
    main()
