# -*- coding: utf-8 -*-

import string
import re

# -----------------------------------------------------------------------------
#  Precompiled regular expressions
# -----------------------------------------------------------------------------

RegexCamelSnake1 = re.compile(r'([^_])([A-Z][a-z]+)')
RegexCamelSnake2 = re.compile('([a-z0-9])([A-Z])')
RegexVhdlLabel = re.compile('[^A-Za-z0-9_]')

# -----------------------------------------------------------------------------
#  Jinja Filters
# -----------------------------------------------------------------------------

def snakecase(label, separator='_'):
    """Transformes camel case label to spaced lower case (snaked) label.
    >>> snakecase('CamelCaseLabel')
    'camel_case_label'
    """
    subbed = RegexCamelSnake1.sub(r'\1{sep}\2'.format(sep=separator), label)
    return RegexCamelSnake2.sub(r'\1{sep}\2'.format(sep=separator), subbed).lower()

def vhdl_label(label):
    """Return normalized VHDL label for signal or instance names.
    >>> vhdl_label('001FooBar.value__@2_')
    'd001_foo_bar_value_2'
    """
    label = RegexVhdlLabel.sub('_', label.strip()) # Replace unsave characters by underscore.
    # Suppress multible underlines (VHDL spec)
    label = re.sub(r'[_]+', r'_', label)
    # Suppress leading/trailing underlines (VHDL spec)
    label = label.strip('_')
    # Prepend char if starts with digit (starting with underline not allowed in VHDL spec).
    if label[0] in string.digits:
        label = ''.join(('d', label))
    return snakecase(label)

def vhdl_expression(expression):
    """Return safe VHDL expression string using normalized signals for conditions.
    >>> vhdl_expression('(singleMu_1 and doubleMu_2)')
    '( single_mu_1 and double_mu_2 )'
    """
    expression = re.sub(r'([\(\)])', r' \1 ', expression) # separate braces
    expression = re.sub(r'[\ ]+', r' ', expression) # suppress multiple spaces
    tokens = []
    for token in expression.split():
        if token not in ['(', ')']:
            token = vhdl_label(token)
        tokens.append(token)
    return ' '.join(tokens)

def expr2html(expression):
    """Returns HTML formatted expression representation.
    Applied CSS classes: .function, .curl, .keyword
    """
    rules = (
        (r',',
         r', '),
        (r'(dist|comb|mass|mass_inv|mass_trv|dist_orm|comb_orm|mass_inv_orm|mass_trv_orm)(\{)([^\}]*)(\})',
         r'<span class="function">\1</span><span class="curl">\2</span>\3<span class="curl">\4</span>'),
        (r'\b(AND|OR|XOR|NOT)\b',
         r'<span class="keyword">\1</span>'),
    )
    for pattern, repl in rules:
        expression = re.sub(pattern, repl, expression)
    return expression

def vhdl2html(expression):
    """Returns HTML formatted VHDL expression representation.
    Applied CSS classes: .vhdlsig, .vhdlop
    """
    rules = (
        (r'\b([a-zA-Z_][a-zA-Z0-9_]*[0-9]+)\b',
         lambda match: '<span class="vhdlsig">{0}</span>'.format(match.group(1))),
        (r'\b(and|or|xor|not|AND|OR|XOR|NOT)\b',
         lambda match: '<span class="vhdlop">{0}</span>'.format(match.group(1).lower())),
    )
    for pattern, repl in rules:
        expression = re.sub(pattern, repl, expression)
    return expression
