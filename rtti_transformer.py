import ast
import astunparse
from rtti import Rtti
import itertools
import os

class RttiTransformer(ast.NodeTransformer):
    _output_filename_suffix = "PyQt6ToCpp"
    _scope_node_types = (ast.If, ast.For, ast.While, ast.With, ast.FunctionDef, ast.ClassDef, ast.Module)
    _anon_scope_node_types = (ast.If, ast.For, ast.While, ast.With)
    
    def __init__(self, app_entry_filename: str):
        super().__init__()
        self._parents = {}
        self._entryModuleName = app_entry_filename
        
    def _get_scope_siblings(self, node, include_node=True, upto_node=False):
        """
        Returns a list of sibling nodes for the given node within its parent.
        If the node has no parent or is not found within the parent's children,
        an empty list is returned.
        """
        parent = self.parent(node)        
        for child in self._scope_child_nodes(parent):
            if include_node or child is not node:
                yield child
            if upto_node:
                if child is node:
                    break
    
    def _scope_child_nodes(self, parent):
        child_nodes = list(ast.iter_child_nodes(parent))
        if not isinstance(parent, ast.If):
            return child_nodes
        return itertools.chain(child_nodes, parent.orelse)
            
    def _count_anon_scopes_up_to_node_pos(self, node, scope_type=None):
        if scope_type is None:
            scope_type = type(node)
        count = -1
        siblings = self._get_scope_siblings(node, upto_node=True)
        for sibling in siblings:
            if isinstance(sibling, scope_type):
                count += 1
            if sibling is node:
                break
        return count
        
    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            self._parents[child] = node
        return super().generic_visit(node)
            
    def parent(self, node):
        return self._parents.get(node, None)
    
    def scope(self, node) -> tuple:
        ancestor = node
        scope = []
        while (ancestor := self.parent(ancestor)) is not None:
            if isinstance(ancestor, self._scope_node_types):
                scope = [ancestor] + scope
        return tuple(scope)
    
    def scoped_name(self, node) -> str:
        scope_str = ''               
        for outer_scope in self.scope(node):
            if isinstance(outer_scope, ast.If):
                count = self._count_anon_scopes_up_to_node_pos(outer_scope)                
                scope_str += f'{outer_scope.__class__.__name__}{count}'
                
                if self._has_ancestor_in(outer_scope.orelse, node):
                    scope_str += "Else"
                    
            elif isinstance(outer_scope, self._anon_scope_node_types):
                count = self._count_anon_scopes_up_to_node_pos(outer_scope)                
                scope_str += f'{outer_scope.__class__.__name__}{count}'
            elif isinstance(outer_scope, ast.Module):
                scope_str += f'{self.module_name()}'
            else:
                scope_str += f'{self.ident(outer_scope)}'
        return f"{scope_str}{node.id}"
    
    def _has_ancestor_in(self, list_, node):
        for x in list_:
            if self._is_ancestor_of(node, query=x):
                return True
        return False
    
    def _is_ancestor_of(self, node, query):
        parent = node
        while (parent := self.parent(parent)) is not None:
            if parent is query:
                return True
        return False
    
    def ident(self, node):
        if isinstance(node, ast.Module):
            return self.module_name()
        if isinstance(node, ast.FunctionDef):
            return node.name
        elif isinstance(node, ast.ClassDef):
            return node.name

    def module_name(self):
        if self._entryModuleName is None:
            return ""
        return self._entryModuleName
        
    def visit_Assign(self, node):
        # Wraps all assignments with a custom function call
        self.generic_visit(node)
        scoped_names = []
        
        for target in node.targets:
            scoped_names.append(self.scoped_name(target))
            
        scoped_names = [ast.Constant(value=s, kind=None) for s in scoped_names]
        
        wrapped_value = ast.Call(
                func=ast.Name(id='record_rtti', ctx=ast.Load()),
                args=[
                    node.value,
                    ast.List(elts=scoped_names,
                             ctx=ast.Load())               
                ],
                keywords=[]
            )
        wrapped_value = ast.copy_location(wrapped_value, node.value)
        new_node = ast.Assign(targets=node.targets, value=wrapped_value)
        return  new_node #ast.copy_location(new_node, node)
    
    def app_entry_filename(self):
        return self._entryModuleName


def record_rtti(values, scoped_names):
    # TODO put on mutex-lock
    if len(scoped_names) == 1:
        vals = [values]
    else:
        vals = values
        
    for k, val in enumerate(vals):
        Rtti.add_type(scoped_names[k], type(val))
        
    return values


if __name__ == '__main__':
    source_code = """
class MyClass:
    def test(self):
        x = 10
        if x != 10:
            y = x + 5
            while x >= 10:
                y = x + 5
                break
        elif x == 11:
            z = 11 + 2
        else:
            y = x + 6
        if x != 10:
            y = x + 5
            while x >= 10:
                y = x + 5
                break
        elif x == 11:
            z = 11 + 2
        else:
            y = x + 6            
            
        return x
o = MyClass()
o.test()
    """
    
    # Parse the source code
    parsed_ast = ast.parse(source_code)
    
    # Transform the AST
    transformer = RttiTransformer(app_entry_filename='rtti_xformer_test1.py')
    new_ast = transformer.visit(parsed_ast)
    #ast.fix_missing_locations(new_ast)
    
    #print(astor.dump_tree(new_ast))
    # Convert AST back to source code
    modified_code = astunparse.unparse(new_ast)
    print(modified_code)
    
    # Execute the modified code
    globals_dict = {'record_rtti': record_rtti, 'Rtii' : Rtti}
    exec(modified_code, globals_dict)
    
    print(Rtti.types())