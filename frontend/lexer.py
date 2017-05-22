'''
Tokens and lexer for Pascal-1973.

Lexer rules originally taken from:
  http://www.pascal-central.com/docs/pascal1973.pdf
'''
from __future__ import absolute_import, print_function

import sys
import os

from ply import lex

from frontend import log

QUOTE = r'(\'|")'

tokens = ('AND',
           'ARRAY',
           'ASSIGNMENT',
           'BINDIGSEQ',
           'CASE',
           'CHAR',
           'COLON',
           'COMMA',
           'COMMENT',
           'CONST',
           'DIGSEQ',
           'DIV',
           'DO',
           'DOT',
           'DOTDOT',
           'DOWNTO',
           'ELSE',
           'END',
           'EQUAL',
           'FOR',
           'FORWARD',
           'FUNCTION',
           'GE',
           'GOTO',
           'GT',
           'HEXDIGSEQ',
           'IDENTIFIER',
           'IF',
           'IN',
           'LABEL',
           'LBRAC',
           'LE',
           'LPAREN',
           'LT',
           'MINUS',
           'MOD',
           'NIL',
           'NOT',
           'NOTEQUAL',
           'OCTDIGSEQ',
           'OF',
           'OR',
           'OTHERWISE',
           'PACKED',
           'PBEGIN',
           'PFILE',
           'PLUS',
           'PROCEDURE',
           'PROGRAM',
           'RBRAC',
           'REALNUMBER',
           'RECORD',
           'REPEAT',
           'RPAREN',
           'SEMICOLON',
           'SET',
           'SLASH',
           'STAR',
           'STARSTAR',
           'STRING',
           'THEN',
           'TO',
           'TYPE',
           'UNTIL',
           'UPARROW',
           'UNPACKED',
           'VAR',
           'WHILE',
           'WITH')

reserved_keywords = {
    'and':        'AND',
    'array':      'ARRAY',
    'begin':      'PBEGIN',
    'case':       'CASE',
    'const':      'CONST',
    'div':        'DIV',
    'do':         'DO',
    'downto':     'DOWNTO',
    'else':       'ELSE',
    'end':        'END',
    'file':       'PFILE',
    'for':        'FOR',
    'forward':    'FORWARD',
    'function':   'FUNCTION',
    'goto':       'GOTO',
    'if':         'IF',
    'in':         'IN',
    'label':      'LABEL',
    'mod':        'MOD',
    'nil':        'NIL',
    'not':        'NOT',
    'of':         'OF',
    'or':         'OR',
    'otherwise':  'OTHERWISE',
    'packed':     'PACKED',
    'procedure':  'PROCEDURE',
    'program':    'PROGRAM',
    'record':     'RECORD',
    'repeat':     'REPEAT',
    'set':        'SET',
    'then':       'THEN',
    'to':         'TO',
    'type':       'TYPE',
    'until':      'UNTIL',
    'var':        'VAR',
    'while':      'WHILE',
    'with':       'WITH'
}

# A string containing ignored characters (spaces and tabs).
t_ignore = ' \t\r\x0c'


# pascal1973.pdf Section 2.4
def t_IDENTIFIER(t):
    r"[a-zA-Z]([a-zA-Z0-9])*"
    if t.value.lower() in reserved_keywords:
        t.type = reserved_keywords[t.value.lower()]
    t.endlexpos = t.lexpos + len(t.value)
    return t


# pascal1973.pdf Section 6.1.2
# determined by particular implementations 
# for escape character only support '\t' '\n' and '\\'
def t_CHAR(t):
    r"(\'(([^\\\'])|(\\[\\tn]))\')"
    t.value = t.value[1:-1]
    t.endlexpos = t.lexpos + len(t.value)
    return t


# pascal1973.pdf Section 2.4
# Allowed paired \' in string
def t_STRING(t):
    r"(\'((\'(([^\\\'])|(\\[\\tn]))*\')|((([^\\\'])|(\\[\\tn]))*))*\')"
    escaped = 0
    s = t.value[1:-1]
    new_str = ""
    for i in range(0, len(s)):
        c = s[i]
        if escaped:
            if c == "n":
                c = "\n"
            elif c == "t":
                c = "\t"
            new_str += c
            escaped = 0
        else:
            if c == "\\":
                escaped = 1
            else:
                new_str += c

    t.endlexpos = t.lexpos + len(t.value)
    t.value = new_str

    return t


# Pascal 1973 do not support comments.
# This is an extension.
def t_COMMENT(t):
    r"(?s)(\(\*.*?\*\))|({[^}]*})"
    t.lexer.lineno += (t.value.count("\n"))
    t.endlexpos = t.lexpos + len(t.value)


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.endlexpos = t.lexpos + len(t.value)


# pascal1973.pdf Section 2.4 and 6.1.2
def t_REALNUMBER(t):
    r"(\d+\.\d+([eE][\+-]\d+)?)|(\d+[eE][\+-]\d+)"
    t.endlexpos = t.lexpos + len(t.value)
    return t


# Pascal 1973 do not support hexadecimal number literal.
# This is an extension. 
def t_HEXDIGSEQ(t):
    r'(?i)[0-9][0-9a-f]*H'
    t.endlexpos = t.lexpos + len(t.value)
    return t


# Pascal 1973 do not support octal number literal.
# This is an extension.
def t_OCTDIGSEQ(t):
    r'[0-7]+Q'
    t.endlexpos = t.lexpos + len(t.value)
    return t


# Pascal 1973 do not support binary number literal.
# This is an extension.
def t_BINDIGSEQ(t):
    r'[01]+B'
    t.endlexpos = t.lexpos + len(t.value)
    return t


# pascal1973.pdf Section 2.4 
# leading zeros are allowed.
def t_DIGSEQ(t):
    r'[0-9]+'
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_ASSIGNMENT(t):
    r":="
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_STARSTAR(t):
    r"\*\*"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_DOTDOT(t):
    r"\.\."
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_GE(t):
    r"\>\="
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_NOTEQUAL(t):
    r"\<\>"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_LE(t):
    r"\<\="
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_COLON(t):
    r":"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_COMMA(t):
    r","
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_LBRAC(t):
    r"\["
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_DOT(t):
    r"\."
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_GT(t):
    r"\>"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_EQUAL(t):
    r"\="
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_LPAREN(t):
    r"\("
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_LT(t):
    r"\<"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_MINUS(t):
    r"\-"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_PLUS(t):
    r"\+"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_RBRAC(t):
    r"\]"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_RPAREN(t):
    r"\)"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_SEMICOLON(t):
    r";"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_SLASH(t):
    r"/"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_STAR(t):
    r"\*"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_UPARROW(t):
    r"\^"
    t.endlexpos = t.lexpos + len(t.value)
    return t


# Error handling rule
def t_error(t):
    log.e("token", "Illegal character '%s'" % t.value[0])


def lexer(debug=False):
    if debug:
        logger = lex.PlyLogger(sys.stderr)
    else:
        logger = lex.NullLogger()

    tab = "frontend.lextable"
    mod = sys.modules[__name__]
    return lex.lex(debuglog=logger,
                   errorlog=logger,
                   optimize=1,
                   lextab=tab,
                   outputdir=os.path.dirname(__file__),
                   module=mod)
