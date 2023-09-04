from jinja2 import pass_context, pass_environment, Environment, meta
from jinja2.runtime import Context
from jinja2.filters import do_mark_safe
from .global_function import exp_env
import subprocess

mapping = {
    r"`b`*`h`=": r"$b\times h=`b`\mm\times `h`\mm$",
    r"`_Md`=": r"$\Md=`_Md`\kNm$",
    r"`_As`=": r"$\As=`_As`\mmsq$",
    r"`_gammao`=": r"$\gammao=`_gammao`$",
    r"`_gammao`*`_Md`=": r"$M=\gammao\times \Md=`_gammao`\times `_Md`=`result` `unit`$",
    r"rho=`_As`/(`b`*`ho`)[-1]=  ,per[100]>? `rhom`= ,per": r"""
\begin{align*}
\rho=\frac{\As}{b \ho}=\frac{`_As`}{`b`\times `ho`}=0.81913\%\leq \rhom=`rhom`\%
\end{align*}""",
    r"`M`=": r"$M=`M`\kNm$"
}


class CalcProcess:
    def __init__(self, process, result, unit):
        self.process = process
        self.result = result
        self.unit = unit

    @property
    def expression(self):
        return self.process


class EquationProcess:
    def __init__(self, equation='', process='', result='', final_result=''):
        self.equation = equation
        self.process = process
        self.result = result
        self.final_result = final_result


@pass_context
def calc(ctx: Context, expression: str, unit=None, assign=False):
    ast = exp_env.parse(expression)
    vars_in_exp = meta.find_undeclared_variables(ast)
    key_value = {var_name: ctx.vars.get(var_name) for var_name in vars_in_exp }
    print("==================================")
    print(expression)
    print(key_value)
    if assign:
        calc_process = CalcProcess(
            process=do_mark_safe(exp_env.from_string(mapping.get(expression)).render({**key_value, 'result':'XXXX', 'unit':unit})),
            result='XXXX',
            unit=unit
        )
        print(calc_process.expression)
        return calc_process
    result = do_mark_safe(exp_env.from_string(mapping.get(expression.strip())).render(**key_value))
    print(result)
    return result


@pass_context
def calc_equation(ctx: Context, expr, **kwargs):
    mapping = {
        '123': {
            'equation': r'$$ x^2+2x+3=0$$',
            'process': r'$$\Delta = b^2-4ac=2^2-4 \texttimes 1 \texttimes 3 = -8$$',
            'result': '-8',
            'final_result': r'',
        },
        '132': {
            'equation': r'$$ x^2+3x+2=0$$',
            'process': r'$$\Delta = b^2-4ac=3^2-4 \texttimes 1 \texttimes 2 = 1$$',
            'result': '1',
            'final_result': r"""
$$x_1= \frac{-b+\sqrt{ b^2-4ac}}{2a}=\frac{-3+\sqrt{ 3^2-4 \texttimes 1 \texttimes 2}}{2\texttimes 1} = -1	$$
$$x_2= \frac{-b-\sqrt{ b^2-4ac}}{2a}=\frac{-3-\sqrt{ 3^2-4 \texttimes 1 \texttimes 2}}{2\texttimes 1} = -2	$$
            """,
        },
        '121': {
            'equation': r'$$ x^2+2x+1=0$$',
            'process': r'$$\Delta = b^2-4ac=2^2-4 \texttimes 1 \texttimes 1 = 0$$',
            'result': '0',
            'final_result': r"$$x_1=x_2= \frac{-b}{2a}=\frac{-2}{2\texttimes 1} = -1	$$",
        },
    }

    # ast = exp_env.parse(expr)
    # vars_in_exp = meta.find_undeclared_variables(ast)
    # key_value = {var_name: ctx.vars.get(var_name) for var_name in vars_in_exp}
    # key = '{}{}{}'.format(kwargs.get('a'), kwargs.get('b'), kwargs.get('c'))
    subprocess.call()
    equation_process = EquationProcess(
        **(mapping.get(key, {}))
    )
    print(mapping.get(key, {}))
    print(equation_process.final_result)
    return equation_process
