import ast
import astor

class UniqueNameTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        # A counter to generate unique suffixes.
        self.counter = 0
        # Stack of scopes (each a dict mapping original names to unique names)
        self.scope_stack = [{}]  # global scope

    def new_name(self, original_name, scope_stack):
        # Create a new unique name by appending a unique counter.
        new = f"{"__".join(scope_stack)}__{original_name}"
        self.counter += 1
        return new

    def current_scope(self):
        return self.scope_stack[-1]

    def lookup(self, name):
        # Look up the unique name from innermost to outermost scope.
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None

    def visit_FunctionDef(self, node):
        # Rename the function itself (its binding lives in the outer scope).
        new_func_name = self.new_name(node.name)
        self.current_scope()[node.name] = new_func_name
        node.name = new_func_name

        # Enter a new scope for the function body.
        self.scope_stack.append({})
        # Rename all function arguments.
        for arg in node.args.args:
            new_arg = self.new_name(arg.arg)
            self.current_scope()[arg.arg] = new_arg
            arg.arg = new_arg

        # Process the function body.
        self.generic_visit(node)
        self.scope_stack.pop()
        return node

    def visit_Lambda(self, node):
        # For lambdas, push a new scope and rename the arguments.
        self.scope_stack.append({})
        for arg in node.args.args:
            new_arg = self.new_name(arg.arg)
            self.current_scope()[arg.arg] = new_arg
            arg.arg = new_arg
        self.generic_visit(node)
        self.scope_stack.pop()
        return node

    def visit_ClassDef(self, node):
        # Rename the class name itself.
        new_class_name = self.new_name(node.name)
        self.current_scope()[node.name] = new_class_name
        node.name = new_class_name

        # Classes also introduce a new scope for their body.
        self.scope_stack.append({})
        self.generic_visit(node)
        self.scope_stack.pop()
        return node

    def visit_Name(self, node):
        # For variable bindings (Store context) create or reuse a unique name.
        if isinstance(node.ctx, ast.Store):
            if node.id not in self.current_scope():
                new_id = self.new_name(node.id)
                self.current_scope()[node.id] = new_id
            else:
                new_id = self.current_scope()[node.id]
            node.id = new_id
        # For loads (or deletes), replace with the unique name if it exists.
        elif isinstance(node.ctx, (ast.Load, ast.Del)):
            new_id = self.lookup(node.id)
            if new_id is not None:
                node.id = new_id
            # Else: it may be a global or built-in name. Leave it unchanged.
        return node

    # For targets in assignment nodes (and similar nodes), the Name nodes will be handled by visit_Name.
    def visit_Assign(self, node):
        self.generic_visit(node)
        return node

    def visit_AugAssign(self, node):
        self.generic_visit(node)
        return node

    def visit_AnnAssign(self, node):
        self.generic_visit(node)
        return node

# Example source code
source_code = """
a = 10
b = 20

def foo(x, y):
    z = x + y + a
    return z

class MyClass:
    def method(self, param):
        value = param * 2
        return value
"""

# Parse the source code into an AST.
parsed_ast = ast.parse(source_code)

# Transform the AST.
transformer = UniqueNameTransformer()
new_ast = transformer.visit(parsed_ast)
ast.fix_missing_locations(new_ast)

# Convert the AST back into source code.
modified_code = astor.to_source(new_ast)
print(modified_code)

# Optionally, execute the transformed code.
globals_dict = {}
exec(modified_code, globals_dict)
