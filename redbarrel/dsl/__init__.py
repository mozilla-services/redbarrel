from redbarrel.dsl.yacc import yacc


def build_ast(code, debug=False):
    return yacc.parse(code, debug=debug)
