""" Building a interpreter."""
import pytest

from collections import OrderedDict

INTEGER = "INTEGER"
REAL = "REAL"
INTEGER_CONST = "INTEGER_CONST"
REAL_CONST = "REAL_CONST"
PLUS = "PLUS"
MINUS = "MINUS"
MUL = "MUL"
INTEGER_DIV = "INTEGER_DIV"
FLOAT_DIV = "FLOAT_DIV"
LPAREN = "LPAREN"
RPAREN = "RPAREN"
ID = "ID"
ASSIGN = "ASSIGN"
BEGIN = "BEGIN"
END = "END"
SEMI = "SEMI"
DOT = "DOT"
PROGRAM = "PROGRAM"
VAR = "VAR"
COLON = "COLON"
COMMA = "COMMA"
EOF = "EOF"
PROCEDURE = "PROCEDURE"


class Token:
    def __init__(self, type, value):
        #: token type
        self.type = type
        #: token value
        self.value = value

    def __str__(self):
        """ String representation of the class instance.

        Examples:
            Token(INTEGER, 3)
            Token(PLUS, '+')
            Token(MUL, '*')
        """
        return f"Token({self.type}, {repr(self.value)})"

    def __repr__(self):
        return self.__str__()


class Symbol:
    def __init__(self, name, type=None):
        self.name = name
        self.type = type


class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super(BuiltinTypeSymbol, self).__init__(name)

    def __str__(self):
        return self.name

    __repr__ = __str__


class VarSymbol(Symbol):
    def __init__(self, name, type):
        super(VarSymbol, self).__init__(name, type)

    def __str__(self):
        return f"<{self.name}:{self.type}>"

    __repr__ = __str__


class SymbolTable:
    def __init__(self):
        self._symbols = OrderedDict()
        self._init_builtins()

    def _init_builtins(self):
        self.define(BuiltinTypeSymbol("INTEGER"))
        self.define(BuiltinTypeSymbol("REAL"))

    def __str__(self):
        s = "Symbols: {symbols}".format(
            symbols=[value for value in self._symbols.values()]
        )
        return s

    __repr__ = __str__

    def define(self, symbol):
        print("Define: %s" % symbol)
        self._symbols[symbol.name] = symbol

    def lookup(self, name):
        print("Lookup: %s" % name)
        symbol = self._symbols.get(name)
        return symbol


RESERVED_KEYWORDS = {
    "PROGRAM": Token("PROGRAM", "PROGRAM"),
    "VAR": Token("VAR", "VAR"),
    "DIV": Token("INTEGER_DIV", "DIV"),
    "INTEGER": Token("INTEGER", "INTEGER"),
    "REAL": Token("REAL", "REAL"),
    "BEGIN": Token("BEGIN", "BEGIN"),
    "END": Token("END", "END"),
    "func": Token("PROCEDURE", "func"),
}


class Lexer:
    def __init__(self, text):
        """ Receive the input string from client."""
        self.text = text
        #: pos is an index in self.text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception(f"Invalid operator: {self.current_char}")

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            # Indicating EOF
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        """ Used to look one character ahead without advancing."""
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char != "}":
            self.advance()
        self.advance()  # The closing curly brace

    def number(self):
        """ Return a (multidigit) integer or float consumed from the input."""
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == ".":
            result += self.current_char
            self.advance()

            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

            token = Token("REAL_CONST", float(result))
        else:
            token = Token("INTEGER_CONST", int(result))

        return token

    def _id(self):
        """ Handles identifiers and reserved keywords."""
        result = ""
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()
        token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token

    def get_next_token(self):
        """ Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == "{":
                self.advance()
                self.skip_comment()
                continue

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == ":" and self.peek() == "=":
                self.advance()
                self.advance()
                return Token(ASSIGN, ":=")

            if self.current_char == ";":
                self.advance()
                return Token(SEMI, ";")

            if self.current_char == ":":
                self.advance()
                return Token(COLON, ":")

            if self.current_char == ",":
                self.advance()
                return Token(COMMA, ",")

            if self.current_char == "+":
                self.advance()
                return Token(PLUS, "+")

            if self.current_char == "-":
                self.advance()
                return Token(MINUS, "-")

            if self.current_char == "*":
                self.advance()
                return Token(MUL, "*")

            if self.current_char == "/":
                self.advance()
                return Token(FLOAT_DIV, "/")

            if self.current_char == "(":
                self.advance()
                return Token(LPAREN, "(")

            if self.current_char == ")":
                self.advance()
                return Token(RPAREN, ")")

            if self.current_char == ".":
                self.advance()
                return Token(DOT, ".")

            self.error()
        return Token(EOF, None)


class AST:
    """ Abstract Syntax Tree."""

    pass


class BinOp(AST):
    """ Binary Operator."""

    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class UnaryOp(AST):
    """ Unary Operator. (e.g. '-2')."""

    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Compound(AST):
    """Represents a 'BEGIN ... END' block"""

    def __init__(self):
        self.children = []


class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    """ The Var node is constructed out of ID token."""

    def __init__(self, token):
        self.token = token
        self.value = token.value


class NoOp(AST):
    pass


class Program(AST):
    def __init__(self, name, block):
        self.name = name
        self.block = block


class Block(AST):
    def __init__(self, declarations, compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement


class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node


class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class ProcedureDecl(AST):
    def __init__(self, proc_name, block_node):
        self.proc_name = proc_name
        self.block_node = block_node


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        #: current_token instance
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception(f"Syntax Error character: {self.lexer.pos}")

    # Stream of tokens
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def program(self):
        """ Program : compound_statement DOT"""
        self.eat(PROGRAM)
        var_node = self.variable()
        prog_name = var_node.value
        self.eat(SEMI)
        block_node = self.block()
        program_node = Program(prog_name, block_node)
        self.eat(DOT)
        return program_node

    def block(self):
        """ block : declarations compound_statement"""
        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes, compound_statement_node)
        return node

    def declarations(self):
        declarations = []
        if self.current_token.type == VAR:
            self.eat(VAR)
            while self.current_token.type == ID:
                var_decl = self.variable_declaration()
                declarations.extend(var_decl)
                self.eat(SEMI)

        while self.current_token.type == PROCEDURE:
            self.eat(PROCEDURE)
            proc_name = self.current_token.value
            self.eat(ID)
            self.eat(SEMI)
            block_node = self.block()
            proc_decl = ProcedureDecl(proc_name, block_node)
            declarations.append(proc_decl)
            self.eat(SEMI)

        return declarations

    def variable_declaration(self):
        """ variable_declaration : ID (COMMA ID)* COLON type_spec"""
        var_nodes = [Var(self.current_token)]  # first ID
        self.eat(ID)

        while self.current_token.type == COMMA:
            self.eat(COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(ID)

        self.eat(COLON)

        type_node = self.type_spec()
        var_declarations = [VarDecl(var_node, type_node) for var_node in var_nodes]
        return var_declarations

    def type_spec(self):
        """ type_spec : INTEGER
                      | REAL
        """
        token = self.current_token
        if self.current_token.type == INTEGER:
            self.eat(INTEGER)
        else:
            self.eat(REAL)
        node = Type(token)
        return node

    def compound_statement(self):
        """ compound_statement : BEGIN statement_list END"""
        self.eat(BEGIN)
        nodes = self.statement_list()
        self.eat(END)

        root = Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def statement_list(self):
        node = self.statement()

        results = [node]

        while self.current_token.type == SEMI:
            self.eat(SEMI)
            results.append(self.statement())

        return results

    def statement(self):
        if self.current_token.type == BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
        return node

    def variable(self):
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def empty(self):
        """ An empty production."""
        return NoOp()

    def expr(self):
        """ Arithmetic expression parser / interpreter.

        expr -> INTEGER PLUS INTEGER.
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def term(self):
        """ term : factor ((MUL | DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (MUL, INTEGER_DIV, FLOAT_DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == INTEGER_DIV:
                self.eat(INTEGER_DIV)
            elif token.type == FLOAT_DIV:
                self.eat(FLOAT_DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        """ factor : INTEGER | LPAREN expr RPAREN."""
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INTEGER_CONST:
            self.eat(INTEGER_CONST)
            return Num(token)
        elif token.type == REAL_CONST:
            self.eat(REAL_CONST)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        else:
            node = self.variable()
            return node

    def parse(self):
        node = self.program()
        if self.current_token.type != EOF:
            self.error()

        return node


class NodeVisitor:
    def visit(self, node):
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method.")


class SymbolTableBuilder(NodeVisitor):
    def __init__(self):
        self.symtab = SymbolTable()

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Num(self, node):
        pass

    def visit_UnaryOp(self, node):
        self.visit(node.expr)

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.symtab.lookup(type_name)
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)
        self.symtab.define(var_symbol)

    def visit_Assign(self, node):
        var_name = node.left.value
        var_symbol = self.symtab.lookup(var_name)
        if var_symbol is None:
            raise NameError(repr(var_name))

        self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        var_symbol = self.symtab.lookup(var_name)
        if var_symbol is None:
            raise NameError(f"name repr(var_name) not defined")

    def visit_ProcedureDecl(self, node):
        pass


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.GLOBAL_SCOPE = {}

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        # Do Nothing
        pass

    def visit_Type(self, node):
        # Do Nothing
        pass

    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == INTEGER_DIV:
            return self.visit(node.left) // self.visit(node.right)
        elif node.op.type == FLOAT_DIV:
            return float(self.visit(node.left)) / float(self.visit(node.right))

    def visit_Num(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        """ Interpret unary nodes."""
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        var_value = self.GLOBAL_SCOPE.get(var_name)
        if var_value is None:
            raise NameError(repr(var_name))
        else:
            return var_value

    def visit_NoOp(self, node):
        pass

    def visit_ProcedureDecl(self, node):
        pass

    def interpret(self):
        tree = self.parser.parse()
        if tree is None:
            return ""
        return self.visit(tree)


def main():
    import sys

    text = open(sys.argv[1], "r").read()

    lexer = Lexer(text)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    interpreter.interpret()
    for k, v in sorted(interpreter.GLOBAL_SCOPE.items()):
        print(f"{k} = {v}")


@pytest.mark.parametrize(
    "case, expected", [("3 * 2 + 2 / 2", 7.0), ("3 * (2 + 2) / 2", 6.0)]
)
def test_associativity(case, expected):
    """ Test the operators are called in the correct order."""
    lexer = Lexer(case)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    assert result == expected


if __name__ == "__main__":
    main()
