import re
from graphviz import Digraph

class Node:
    def __init__(self, id, label=None):
        self.id = str(id)
        self.label = label
        self.edges = []

class Edge:
    def __init__(self, target, label):
        self.target = target
        self.label = pre_order_to_in_order(label)

class CFG:
    def __init__(self):
        self.nodes = []
        self.start = None
        self.end = None

    def add_node(self, node):
        self.nodes.append(node)
        return node

    def add_edge(self, source, target, label):
        edge = Edge(target, label)
        source.edges.append(edge)

def parse_s_expression(s_expr):
    tokens = re.findall(r'\(|\)|[^\s()]+', s_expr)
    def parse():
        if tokens[0] == '(':
            tokens.pop(0)
            L = []
            while tokens[0] != ')':
                L.append(parse())
            tokens.pop(0)
            return L
        else:
            return tokens.pop(0)
    return parse()

def create_cfg(ast):
    cfg = CFG()
    node_counter = 0

    def create_node(label=None):
        nonlocal node_counter
        node_counter += 1
        node = Node(node_counter, label)
        return cfg.add_node(node)

    def process_statement(stmt, entry, exit):
        if isinstance(stmt, list):
            if stmt[0] == 'while':
                condition = stmt[1]
                body = stmt[2]
                loop_entry = create_node("while")
                #loop_exit = create_node()
                cfg.add_edge(entry, loop_entry, '')
                cfg.add_edge(loop_entry, exit, ["~", condition])
                body_entry, body_exit = process_statement(body, loop_entry, loop_entry)
                return entry, exit
            elif stmt[0] == 'if':
                condition = stmt[1]
                then_branch = stmt[2]
                else_branch = stmt[3] if len(stmt) > 3 else None
                if_entry = create_node("if")
                then_entry = create_node("then")
                cfg.add_edge(entry, if_entry, '')
                cfg.add_edge(if_entry, then_entry, condition)
                process_statement(then_branch, then_entry, exit)
                if else_branch:
                    else_entry = create_node("else")
                    cfg.add_edge(if_entry, else_entry, ["~", condition])
                    process_statement(else_branch, else_entry, exit)
                else:
                    cfg.add_edge(if_entry, exit, ["~", condition])
                return if_entry, exit
            elif stmt[0] == 'begin':
                last_node = entry
                first_node = None
                num_stmt = len(stmt)
                for i in range(1, num_stmt):
                    s = stmt[i]
                    mid_node = (create_node() if i+1<num_stmt else exit)
                    if first_node is None:
                        first_node, last_node = process_statement(s, last_node, mid_node)
                    else:
                        _, last_node = process_statement(s, last_node, mid_node)
                return first_node, last_node
            elif stmt[0] == 'error':
                error_node = create_node("error")
                cfg.add_edge(entry, error_node, '')
                return error_node, error_node
            else:
                cfg.add_edge(entry, exit, stmt)
                return entry, exit
        else:
            cfg.add_edge(entry, exit, stmt)
            return entry, exit

    cfg.start = create_node("start")
    cfg.end = create_node("end")
    process_statement(ast, cfg.start, cfg.end)
    return cfg

def visualize_cfg(cfg, filename='cfg'):
    dot = Digraph(comment='Control Flow Graph')
    dot.attr(rankdir='TB')

    for node in cfg.nodes:
        dot.node(node.id, f"s{node.id}" if node.label is None else node.label)
        for edge in node.edges:
            dot.edge(node.id, edge.target.id, edge.label)

    dot.render(filename, view=False, format='png')

def pre_order_to_in_order(expr):
    if not isinstance(expr, list):
        return str(expr)
    
    if len(expr) == 2:
        op, operand = expr
        return f"{op}({pre_order_to_in_order(operand)})"
    
    if len(expr) == 3:
        op, left, right = expr
        return f"{pre_order_to_in_order(left)} {op} {pre_order_to_in_order(right)}"
    
    raise ValueError("Invalid expression format")

# Test the new pre_order_to_in_order function
# test_expr = ['=', 'x', ['+', 'y', 1]]
# in_order_expr = pre_order_to_in_order(test_expr)
# print(f"Pre-order: {test_expr}")
# print(f"In-order: {in_order_expr}")

s_expr = """
(begin
  (= x 0)
  (= y 0)
  (while (< i 10)
    (begin
      (if (== (% i 2) 0)
        (= x (+ x i))
        (= y (+ y i)))
      (= i (+ i 1))))
  (= x (+ x 1)))
"""

ast = parse_s_expression(s_expr)
cfg = create_cfg(ast)
visualize_cfg(cfg)