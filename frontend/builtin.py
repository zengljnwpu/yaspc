'''
Implementations of built-in functions in Pascal-86.
'''
from __future__ import absolute_import, print_function

from frontend import typesys
from frontend import log

import llvmlite.ir as ir


builtin = {}


def def_ord(mod):
    ret = ir.IntType(32)
    args = [ir.IntType(8)]
    fnty = ir.FunctionType(ret, args)
    fn = ir.Function(mod, fnty, name='ord')
    
    x, = fn.args
    builder = ir.IRBuilder(fn.append_basic_block('ord.entry'))
    p = builder.alloca(ret)
    pp = builder.bitcast(p, ir.PointerType(ir.IntType(8)))
    builder.store(x, pp)
    builder.ret(builder.load(p))

    return fn


def def_chr(mod):
    ret = ir.IntType(8)
    args = [ir.IntType(32)]
    fnty = ir.FunctionType(ret, args)
    fn = ir.Function(mod, fnty, name='ord')
    
    x, = fn.args
    builder = ir.IRBuilder(fn.append_basic_block('ord.entry'))
    p = builder.alloca(ret)
    pp = builder.bitcast(p, ir.PointerType(ir.IntType(8)))
    builder.store(x, pp)
    builder.ret(builder.load(p))

    return fn


# TODO(Cholerae): odd/succ/pred

# TODO(Cholerae): this definition will return wrong answer, 
# don't know why.

# def def_succ(mod):
#     ret = ir.IntType(32)
#     args = [ir.IntType(32)]
#     fnty = ir.FunctionType(ret, args)
#     fn = ir.Function(mod, fnty, name='ord')
    
#     x, = fn.args
#     builder = ir.IRBuilder(fn.append_basic_block('ord.entry'))
#     p = builder.alloca(ret)
#     pp = builder.bitcast(p, ir.PointerType(ir.IntType(8)))
#     builder.store(x, pp)
#     p_value = builder.load(pp)
#     builder.add(p_value, ir.Constant(args[0], 1))
#     builder.store(p_value, pp)
#     builder.ret(builder.load(p))


def _llvm_to_symtab(type_):
    if isinstance(type_, ir.VoidType):
        return typesys.VoidType()
    elif isinstance(type_, ir.IntType):
        return typesys.SIntType(type_.width)
    elif isinstance(type_, ir.FloatType):
        return typesys.FloatType()
    elif isinstance(type_, ir.DoubleType):
        return typesys.DoubleType()
    elif isinstance(type_, ir.PointerType):
        # Assume all char pointers are strings
        if isinstance(type_.pointee, ir.IntType) and type_.pointee.width == 8:
            return typesys.StringType(0)
        else:
            referee_ty = _llvm_to_symtab(type_.pointee)
            return typesys.ReferenceType(referee_ty)
    else:
        log.e('fn', 'unknown llvm type %s' % type_)


def translate_function(func):
    '''
    Converts a function from the internal symtab format
    into llvmlite format.
    '''
    type_ = func.type.pointee
    ret_ty = _llvm_to_symtab(type_.return_type)

    module = 'frontend'
    name = func.name
    if '.' in name:
        module, name = name.split('.', 1)

    ty = typesys.FunctionType(module, name, ret_ty)

    for i, arg in enumerate(type_.args):
        arg_ty = _llvm_to_symtab(arg)
        arg_name = "arg%d" % i
        param = typesys.ParameterType(arg_name, arg_ty)
        ty.params.append(param)

    return ty
    

def _install_function(ctx, func):
    ty = translate_function(func)
    ctx.install_function(func.name, ty, func)


def f_printf(mod):
    '''libc: formatted output conversion'''
    ret = ir.IntType(32)
    arg = ir.PointerType(ir.IntType(8))

    type_ = ir.FunctionType(ret, [arg], True)
    # avoid DuplicatedNameError
    # TODO(Cholerae): Fix all builtin functions and find a better way.
    if builtin.get('printf') is None:
        builtin['printf'] = ir.Function(mod, type_, 'printf')
    return builtin['printf']


def f_scanf(mod):
    '''libc: input format conversion'''
    ret = ir.IntType(32)
    arg = ir.PointerType(ir.IntType(8))

    type_ = ir.FunctionType(ret, [arg], True)
    if builtin.get('scanf') is None:
        builtin['scanf'] = ir.Function(mod, type_, 'scanf')
    return builtin['scanf']


def f_abs(mod):
    '''libc: compute the absolute value of an integer'''
    ret = ir.IntType()
    args = [ir.IntType()]

    type_ = ir.FunctionType(ret, args)
    return ir.Function(mod, type_, 'abs')


def f_fabs(mod):
    '''libc: absolute value of floating-point number'''
    ret = ir.DoubleType()
    args = [ir.DoubleType()]

    type_ = ir.FunctionType(ret, args)
    return ir.Function(mod, type_, 'fabs')


def f_pow(mod):
    '''libc: power function'''
    ret = ir.DoubleType()
    args = [ir.DoubleType(), ir.DoubleType()]

    type_ = ir.FunctionType(ret, args)
    return ir.Function(mod, type_, 'pow')


def f_round(mod):
    '''libc: round function'''
    ret = ir.DoubleType()
    args = [ir.DoubleType()]
    type_ = ir.FunctionType(ret, args)
    return ir.Function(mod, type_, 'round')


def f_trunc(mod):
    '''libc: trunc function'''
    ret = ir.DoubleType()
    args = [ir.DoubleType()]
    type_ = ir.FunctionType(ret, args)
    return ir.Function(mod, type_, 'trunc')


def f_powf(mod):
    '''libc: power function'''
    ret = ir.FloatType().float()
    args = [ir.FloatType().float(), ir.FloatType().float()]

    type_ = ir.FunctionType(ret, args)
    return ir.Function(mod, type_, 'powf')


def f_sin(mod):
    '''libc: sine function'''
    ret = ir.DoubleType()
    arg = ir.DoubleType()
    type_ = ir.FunctionType(ret, [arg])
    return ir.Function(mod, type_, 'sin')


def f_cos(mod):
    '''libc: cosine function'''
    ret = ir.DoubleType()
    arg = ir.DoubleType()
    type_ = ir.FunctionType(ret, [arg])
    return ir.Function(mod, type_, 'cos')


def f_tan(mod):
    '''libc: tangent function'''
    ret = ir.DoubleType()
    arg = ir.DoubleType()
    type_ = ir.FunctionType(ret, [arg])
    return ir.Function(mod, type_, 'tan')


def f_exp(mod):
    '''libc: base-e exponential function'''
    ret = ir.DoubleType()
    arg = ir.DoubleType()
    type_ = ir.FunctionType(ret, [arg])
    return ir.Function(mod, type_, 'exp')


def f_ln(mod):
    '''libc: natural logarithmic function'''
    ret = ir.DoubleType()
    arg = ir.DoubleType()
    type_ = ir.FunctionType(ret, [arg])
    return ir.Function(mod, type_, 'log')


def f_sqrt(mod):
    '''libc: square root function'''
    ret = ir.DoubleType()
    args = [ir.DoubleType()]

    type_ = ir.FunctionType(ret, args)
    return ir.Function(mod, type_, 'sqrt')


def f_sqrtf(mod):
    '''libc: square root function'''
    ret = ir.FloatType().float()
    args = [ir.FloatType().float()]

    type_ = ir.FunctionType(ret, args)
    return ir.Function(mod, type_, 'sqrtf')


def f_arctan(mod):
    '''libc: arc tangent function'''
    ret = ir.DoubleType()
    arg = ir.DoubleType()
    type_ = ir.FunctionType(ret, [arg])
    return ir.Function(mod, type_, 'atan')


def f_atoi(mod):
    '''libc: convert a string to an integer'''
    ret = ir.IntType(32)
    args = [ir.PointerType(ir.IntType(8))]

    type_ = ir.FunctionType(ret, args)
    return ir.Function(mod, type_, 'atoi')


# TODO(Cholerae): argc and argv
def f_main(mod):
    '''main function'''
    # argc = ir.IntType(32)
    # argv = ir.PointerType(ir.PointerType(ir.IntType(8)))
    # type_ = ir.FunctionType(ir.VoidType(), [argc, argv])
    type_ = ir.FunctionType(ir.VoidType(), [])

    return ir.Function(mod, type_, 'main')


def f_malloc(mod):
    '''libc: allocate heap memory'''
    args = [ir.IntType(64)]
    ret = ir.PointerType(ir.IntType(8))
    type_ = ir.FunctionType(ret, args)
    return ir.Function(mod, type_, 'malloc')


def define_builtinlib(ctx):
    '''
    Defines built-in functions defined by Pascal 1973
    '''
    # _install_function(ctx, def_ord(ctx.module))
    # _install_function(ctx, def_chr(ctx.module))
