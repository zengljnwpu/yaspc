'''
Tokens and lexer for Pascal-1973.

Lexer rules originally taken from:
  http://www.pascal-central.com/docs/pascal1973.pdf
'''

import sys
import os

from ply import lex

from frontend import log


t_QUOTE = r'(\'|")'


tokens = ('AND',
      'ARRAY',
      'BOOLEAN',
      'CASE',
      'CONST',
      'DIV',
      'DO',
      'DOWNTO',
      'ELSE',
      'END',
      'FOR',
      'FORWARD',
      'FUNCTION',
      'GOTO',
      'IF',
      'IN',
      'LABEL',
      'MOD',
      'NIL',
      'NOT',
      'OF',
      'OR',
      'OTHERWISE',
      'PACKED',
      'PBEGIN',
      'PFILE',
      'PROCEDURE',
      'PROGRAM',
      'RECORD',
      'REPEAT',
      'SET',
      'THEN',
      'TO',
      'TYPE',
      'UNTIL',
      'VAR',
      'WHILE',
      'WITH',
      'IDENTIFIER',
      'ASSIGNMENT',
      'COLON',
      'COMMA',
      'DIGSEQ',
      'DOT',
      'DOTDOT',
      'EQUAL',
      'GE',
      'GT',
      'LBRAC',
      'LE',
      'LPAREN',
      'LT',
      'MINUS',
      'NOTEQUAL',
      'PLUS',
      'RBRAC',
      'REALNUMBER',
      'RPAREN',
      'SEMICOLON',
      'SLASH',
      'STAR',
      'STARSTAR',
      'UPARROW',
      
      'COMMENT',
      'CHAR',
      'STRING',
)


reserved_keywords = {
    'and':        'AND',
'array':      'ARRAY',
'boolean':    'BOOLEAN',
'case':       'CASE',
'div':        'DIV',
'do':         'DO',
'downto':     'DOWNTO',
'else':       'ELSE',
'end':        'END',
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
'begin':      'PBEGIN',
'file':       'PFILE',
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
t_IGNORE = ' \t\r\x0c'


# pascal1973.pdf Section 2.4
def t_IDENTIFIER(self, t):
    r"[a-zA-Z]([a-zA-Z0-9])*"
    if t.value.lower() in reserved_keywords:
        t.type = reserved_keywords[t.value.lower()]
    t.endlexpos = t.lexpos + len(t.value)
    return t


# pascal1973.pdf Section 6.1.2
# determined by particular implementations 
# for escape character only support '\t' '\n' and '\\'
def t_CHAR(self, t):
    r"(\'(([^\\\'])|(\\[\\tn]))\')"
    t.value = t.value[1:-1]
    t.endlexpos = t.lexpos + len(t.value)
    return t


# pascal1973.pdf Section 2.4
# Allowed paired \' in string
def t_STRING(self, t):
    r"(\'((\'(([^\\\'])|(\\[\\tn]))*\')|((([^\\\'])|(\\[\\tn]))*))*\')"
    escaped = False
    s = t.value[1:-1]
    new_str = ''
    for i in range(0, len(s)):
        c = s[i]
        if escaped:
            if c == "n":
                c = "\n"
            elif c == "t":
                c = "\t"
            new_str += c
            escaped = False
        else:
            if c == "\\":
                escaped = True
            else:
                new_str += c
    t.endlexpos = t.lexpos + len(t.value)
    t.value = new_str
    return t


# Pascal 1973 do not support comments.
# This is an extension.
def t_COMMENT(self, t):
    r"(?s)(\(\*.*?\*\))|({[^}]*})"
    t.lexer.lineno += (t.value.count("\n"))
    t.endlexpos = t.lexpos + len(t.value)


t_NEWLINE = r'\n+'

# pascal1973.pdf Section 2.4 and 6.1.2
def t_REALNUMBER(self, t):
    r"(\d+\.\d+([eE][\+-]\d+)?)|(\d+[eE][\+-]\d+)"
    t.endlexpos = t.lexpos + len(t.value)
    return t


# Pascal 1973 do not support hexadecimal number literal.
# This is an extension. 
def t_HEXDIGSEQ(self, t):
    r'(?i)[0-9][0-9a-f]*H'
    t.endlexpos = t.lexpos + len(t.value)
    return t


# Pascal 1973 do not support octal number literal.
# This is an extension.
def t_OCTDIGSEQ(self, t):
    r'[0-7]+Q'
    t.endlexpos = t.lexpos + len(t.value)
    return t


# Pascal 1973 do not support binary number literal.
# This is an extension.
def t_BINDIGSEQ(self, t):
    r'[01]+B'
    t.endlexpos = t.lexpos + len(t.value)
    return t


# pascal1973.pdf Section 2.4 
# leading zeros are allowed.
def t_DIGSEQ(self, t):
    r'[0-9]+'
    t.endlexpos = t.lexpos + len(t.value)
    return t


# pascal1973.pdf Section 6.1.2
def t_BOOLEAN(self, t):
    r'true|false'
    t.endlexpos = t.lexpos + len(t.value)
    return t


t_ASSIGNMENT = r':='
t_STARSTAR = r'\*\*'
t_DOTDOT = r'\.\.'
t_GE = r'\>\='
t_NOTEQUAL = '\<\>'
t_LE = r'\<\='
t_COLON = r':'
t_COMMA = r','
t_LBRAC = r'\['
t_RBRAC = r'\]'
t_DOT = r'\.'
t_GT = r'\>'
t_LT = r'\<'
t_EQUAL = r'\='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_MINUS = r'\-'
t_PLUS = r'\+'
t_SEMICOLON = r';'
t_SLASH = r'/'

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

    tab = 'frontend.lextab'
    mod = sys.modules[__name__]
    return lex.lex(debuglog=logger,
                   errorlog=logger,
                   optimize=1,
                   lextab=tab,
                   outputdir=os.path.dirname(__file__),
                   module=mod)
