import re
import sys

tape = [0] * 8
tape_pos = 0

jump_points = {}
macros = {}

char_buffer = []
        
def parse_token(token: str) -> None:
    global tape
    global tape_pos

    global jump_points
    global macros

    if token.startswith('+') or token.startswith('-') and token != '->':
        shift = int(token[1:], 16)
        shift *= -1 if token.startswith('-') else 1

        tape[tape_pos] = (tape[tape_pos] + shift) % 256
    elif token.startswith('~'):
        val = int(token[1:], 16)
        tape[tape_pos] = val % 256
    elif token.startswith('%%'):
        val = min(int(token[2:], 16), 256)
        tape[tape_pos] = (tape[tape_pos] % val)
    elif token == '<-':
        if tape_pos > 0:
            tape_pos -= 1
        else:
            print(f"Error: left bound exceeded.")
            quit(1)
    elif token == '->':
        if tape_pos < len(tape) - 1:
            tape_pos += 1
        else:
            print(f"Error: right bound exceeded.")
            quit(1)
    elif token == '=>':
        tape[tape_pos] = ord(input()[0]) % 256
    elif token == '<=':
        print(chr(tape[tape_pos]), end='')
    elif token == '%>':
        tape[tape_pos] = int(input()) % 256
    elif token == '<%':
        print(tape[tape_pos], end='')
    elif token == '<>':
        print(chr(tape[tape_pos]), end='')
        
        if tape_pos < len(tape) - 1:
            tape_pos += 1
        else:
            print("Error: right bound exceeded.")
            quit(1)
    elif token == '<%>':
        print(tape[tape_pos], end='')

        if tape_pos < len(tape) - 1:
            tape_pos += 1
        else:
            print("Error: right bound exceeded.")
            quit(1)
    elif token == '<<':
        tape_pos = 0
    elif token == '>>':
        tape_pos = len(tape) - 1
    elif token.startswith('&') and '(' in token and ')' in token:
        macro = token[1:token.find('(')]
        macro_def = token[token.find('(') + 1:token.find(')')]

        if macro == "":
            print("Error: empty macro name.")
            quit(1)

        macros[macro] = macro_def
    elif token.startswith('??'):
        if '(' and ')' in token:
            tokens = token[3:token.find(')')].strip().split()

            if tape[tape_pos] != 0:
                for tok in tokens:
                    parse_token(tok)
        else:
            if tape[tape_pos] != 0:
                parse_token(token[2:])
    elif token.startswith('?'):
        if '(' and ')' in token:
            tokens = token[2:token.find(')')].strip().split()

            while tape[tape_pos] != 0:
                for tok in tokens:
                    parse_token(tok)
        else:
            while tape[tape_pos] != 0:
                parse_token(token[1:])
    elif token.startswith('!??'):
        if '(' and ')' in token:
            tokens = token[4:token.find(')')].strip().split()

            if tape[tape_pos] == 0:
                for tok in tokens:
                    parse_token(tok)
        else:
            if tape[tape_pos] == 0:
                parse_token(token[3:])
    elif token.startswith('!?'):
        if '(' and ')' in token:
            tokens = token[3:token.find(')')].strip().split()

            while tape[tape_pos] == 0:
                for tok in tokens:
                    parse_token(tok)
        else:
            while tape[tape_pos] == 0:
                parse_token(token[2:])
    elif re.match("\[.*?\]", token):
        iterations = int(token[1:token.find(']')], 16)

        if iterations <= 0:
            iterations = len(tape) + iterations

        if '(' in token and ')' in token:
            for i in range(iterations):
                for tok in token[token.find('(') + 1:token.find(')')].strip().split():
                    parse_token(tok)
        else:
            for i in range(iterations):
                parse_token(token[token.find(']') + 1:])

    elif re.match('\{.*?\}', token):
        entries = token[1:-1].split(',')
        
        for entry in entries:
            key, value = [int(x, 16) for x in entry.split(':')]

            if tape[tape_pos] == key:
                tape[tape_pos] = value
                break

    elif token.startswith('*'):
        macro = token[1:]

        if macro in macros.keys():

            for token in macros[macro].strip().split():
                parse_token(token)
        else:
            print(f"Error: macro '{macro}' is not defined.")
            quit(1)
    elif token.startswith('@'):
        bookmark = token[1:]
        jump_points[bookmark] = tape_pos
    elif token.startswith('^'):
        bookmark = token[1:]

        if bookmark in jump_points.keys():
            tape_pos = min(jump_points[bookmark], len(tape) - 1)
        else:
            print(f"Error: jump point '{token[1:]}' is not defined.")
            quit(1)
    else:
        print(f"Error: invalid token '{token}'")
        quit(1)

def shell():
    while True:
        text = input("(C* Shell) ")
        parse_line(text, show_tape=True)

def parse_line(text: str, show_tape: bool = False):
    global tape
    global tape_pos
    
    if text.startswith('#'):
        tape_pos = 0
        tape = [int(x, 16) for x in text[1:].strip().split()]
        return
    elif text.startswith('//'):
        return


    tokens = text.split()

    token_index = 0

    while token_index < len(tokens):
        if tokens[token_index].count('(') > 0:
            current_token = ''
            parens = tokens[token_index].count('(')

            #while token_index < len(tokens) and parens > 0:
            #    current_token += tokens[token_index] + ' '
            #    parens += tokens[token_index].count('(') - tokens[token_index].count(')')
            #    token_index += 1

            while token_index < len(tokens) and not ')' in tokens[token_index]:
                current_token += tokens[token_index] + ' '
                token_index += 1

            current_token += tokens[token_index]
            token_index += 1
            parse_token(current_token)
        else:
            parse_token(tokens[token_index])
            token_index += 1

    if show_tape:
        print(f"TAPE: {tape}")

#while True:
#    text = input("(C* Shell) ")
#
#    if text.startswith('#'):
#        tape_pos = 0
#        tape = [int(x) for x in text[1:].strip().split()]
#        continue
#
#
#    tokens = text.split()
#
#    token_index = 0
#
#    while token_index < len(tokens):
#        if tokens[token_index].count('(') > 0:
#            current_token = ''
#            parens = tokens[token_index].count('(')
#
#            #while token_index < len(tokens) and parens > 0:
#            #    current_token += tokens[token_index] + ' '
#            #    parens += tokens[token_index].count('(') - tokens[token_index].count(')')
#            #    token_index += 1
#
#            while token_index < len(tokens) and not ')' in tokens[token_index]:
#                current_token += tokens[token_index] + ' '
#                token_index += 1
#
#            current_token += tokens[token_index]
#            token_index += 1
#            parse_token(current_token)
#        else:
#            parse_token(tokens[token_index])
#            token_index += 1
#
#    print(f"TAPE: {tape}")


fname = sys.argv[1] if len(sys.argv) > 1 else '<stdin>'
lines = []

if fname != '<stdin>':
    with open(fname, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        parse_line(line)
else:
    shell()
