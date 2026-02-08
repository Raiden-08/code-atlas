import tree_sitter_python as tspython 
from tree_sitter import Language, Parser
import os

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)
    
def get_functions_from_file(file_path):
    
    with open(file_path, "rb") as fd:
        source_bytes = fd.read()
        
    tree = parser.parse(source_bytes)
    function = []
    
    traverse_tree(tree.root_node, source_bytes,function,file_path)
    return function

def traverse_tree(node, source_bytes, results, file_path):
    if node.type == "function_definition":
        func_data = extract_function_details(node, source_bytes,file_path)
        if func_data:
            results.append(func_data)
    for child in node.children:
        traverse_tree(child,source_bytes,results, file_path)

def extract_function_details(node, source_bytes,file_path):
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
    func_name = source_bytes[name_node.start_byte : name_node.end_byte].decode("utf-8")
    full_code = source_bytes[node.start_byte : node.end_byte].decode("utf-8")
    docstring = None
    body = node.child_by_field_name("body")
    if body and body.children:
        first_sentence =  body.children[0]
        if first_sentence.type == "expression_statement":
            if first_sentence.children and first_sentence.children[0].type == "string":
                string_node = first_sentence.children[0]
                docstr = source_bytes[string_node.start_byte : string_node.end_byte].decode("utf-8")
                docstring = docstr.strip('\'"')
                
    return {
        "name" : func_name,
        "code" : full_code,
        "docstring" : docstring,
        "filepath" : file_path,
        "line" : node.start_point[0] + 1 
    } 