class Token(object):
    # Token class represents a single token with a type and value
    def __init__(self, atype, avalue):
        self.type = atype
        self.value = avalue

    def __eq__(self, other):
        # Equality check for tokens, either comparing type and value or just type
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return self.type == other

    def __repr__(self):
        # Representation of the token for debugging
        return f"({self.type} {self.value})"

def tokenizer(xs):
    # Converts a string input into a list of tokens
    tokens = []
    symbols = {"(": "lparen", ")": "rparen", "=": "equal", ";": "semi", "+": "op", "-": "op", "*": "op", "/": "op"}
    for x in xs:
        if x.isalpha():
            # Tokenize alphabetic characters as names
            tokens.append(Token("name", x))
        elif x.isdigit():
            # Tokenize numeric characters as numbers
            tokens.append(Token("number", int(x)))
        elif x in symbols.keys():
            # Tokenize symbols based on predefined mapping
            tokens.append(Token(symbols[x], x))
    return tokens

class Parser:
    # Parser class for recursive descent parsing
    def __init__(self, code):
        self.code = code  # List of tokens to parse
        self.i = 0  # Current position in the token list
        self.current = self.code[0]  # Current token

    def next(self):
        # Move to the next token, or set to EOF if at the end
        self.i += 1
        alist = self.code[self.i:self.i + 1] or [Token("eof", object())]
        self.current = alist[0]

    def matching(self, *args):
        # Check if the next tokens match a given sequence or set of possibilities
        for i, arg in enumerate(args):
            if arg is None or arg == self.code[self.i + i]:
                continue
            if isinstance(arg, list):
                if self.code[self.i + i] in arg:
                    continue
            return False
        return True

    def match(self, a):
        # Consume the current token if it matches the given type or value
        if self.current == a or (isinstance(a, list) and self.current in a):
            result = self.current.value
            self.next()
            return result

        raise Exception(f"match error: {a}")

    def parse_expression(self, left=False, op=False):
        # Parse arithmetic expressions with operator precedence
        precedence = {"+": 0, "-": 0, "*": 2, "/": 1}

        # Handle parentheses
        if self.matching("lparen"):
            self.match("lparen")  # Consume '('
            result = self.parse_expression()  # Parse the sub-expression
            self.match("rparen")  # Consume ')'
            if left:
                result = [op, left, result]
            if self.matching("op"):
                op2 = self.match("op")
                return self.parse_expression(result, op2)
            return result

        # Handle numbers or names as terminal nodes
        if self.matching(["name", "number"], ["semi", "rparen"]):
            name_or_number = self.match(["name", "number"])
            if left:
                return [op, left, name_or_number]
            return name_or_number

        # Handle operators with precedence when left operand exists
        if self.matching(["name", "number"], "op") and left:
            name_or_number = self.match(["name", "number"])
            op2 = self.match("op")
            if precedence[op] > precedence[op2]:
                return self.parse_expression([op, left, name_or_number], op2)
            return [op, left, self.parse_expression(name_or_number, op2)]

        # Handle initial operators and operands
        if self.matching(["name", "number"], "op"):
            name_or_number = self.match(["name", "number"])
            op = self.match("op")
            return self.parse_expression(name_or_number, op)

    def parse_assignment(self):
        # Parse assignment statements of the form: name = expression
        if self.matching("name", "equal"):
            var_name = self.match("name")  # Match and consume the variable name
            self.match("equal")  # Match and consume the '=' symbol
            expr = self.parse_expression()  # Parse the right-hand expression
            return ["assign", var_name, expr]  # Return an assignment node

    def parse(self):
        # Parse a single assignment or expression
        if self.matching("name", "equal"):
            return self.parse_assignment()
        return self.parse_expression()

# Example usage
tokens = tokenizer("x = 5 * (1 + 2) + (3 + 4);")
p = Parser(tokens)
result = p.parse()
print(result)  # Output: ['assign', 'x', ['+', ['*', 5, ['+', 1, 2]], ['+', 3, 4]]]
