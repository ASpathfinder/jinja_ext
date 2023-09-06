import json
from . import create_tex_env, ttp_process_ds, ttp_pre_process
from . global_function import exp_env
import subprocess
import click
import tempfile
import sys
import os


@click.command('parse')
@click.option('--ds', help='ds 文件路径')
@click.option('--template', '-t', help='模板文件路径')
@click.option('--output-dir', '-o', help='输出目录')
def render_tex(template, ds, output_dir):
    if not os.path.exists(template):
        print("模板文件 '{}' 不存在".format(template))
        exit(-1)

    if not os.path.exists(ds):
        print("ds 文件 '{}' 不存在".format(ds))
        exit(-1)

    _, tmp_tmpl_path = tempfile.mkstemp(prefix='jinja2-tex-')

    complete = subprocess.run(['preparse.exe', '-s', template, '-o', tmp_tmpl_path], capture_output=True)
    try:
        complete.check_returncode()
    except subprocess.CalledProcessError as e:
        print(e)
        exit(-1)

    abs_path = os.path.abspath(template)
    head, file_name = os.path.split(abs_path)

    tmp_abs_path = os.path.abspath(tmp_tmpl_path)
    tmp_head, tmp_file_name = os.path.split(tmp_abs_path)

    tex_env = create_tex_env(template_folder=[head, tmp_head])
    tex_env.ds_file_path = ds

    # 读取用户自定义 tex 模板，并加入系统预定义的模板内容
    #with open(abs_path, 'r') as f:
    #    tmpl_string = tex_env.get_template('prepare.jinja2').render(user_raw=f.read())

    # 渲染上一步处理过的用户模板
    #template_obj = tex_env.from_string(tmpl_string)

    template_obj = tex_env.get_template(tmp_file_name)

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, file_name + '.tex'), 'w+', encoding='utf8') as f:
        f.write(template_obj.render())


@click.command('preparse')
@click.option('--source-file', '-s', help='模板文件路径')
@click.option('--ttp-template', '-t', default=None, help='模板文件路径')
@click.option('--output-file', '-o', help='输出文件路径')
def pre_parse(source_file, ttp_template, output_file):
    ttp_tmp=r"""
<group name="math_block">
&lt;{{ math_block | re("Math") }}&gt;
</group>

<group name="math_endblock">
&lt;{{ math_endblock | re("/Math") }}&gt;
</group>

<group name="equation">
&lt;{{ equation | re("[^,]+") | exclude("Math") }}{{ comma | re("(\s*,\s*)*") }}{{ unit | re("(\s*[^\s]+\s*)*") }}&gt;
</group>
"""

    ttp_pre_process(source_file, ttp_template if ttp_template else ttp_tmp, output_file)

    return 0


@click.command('texsh')
@click.option('--ds', help='ds 文件路径')
@click.option('--equation', '-e', default=None, help='输入公式')
@click.option('--output-file', '-o', default=None, help='计算结果输出文件路径，不指定则输出到标准输出')
def tex_sh(ds, equation, output_file):
    mapping = {
        r"b*h==": r"$b\times h=`b`\mm\times `h`\mm$",
        r"Md=,kNm": r"$\Md=`Md`\kNm$",
        r"As= ,mmsq": r"$\As=`As`\mmsq$",
        r"gammao=": r"$\gammao=`gammao`$",
        r"M=gammao*Md= ,kNm": r"$M=\gammao\times \Md=`gammao`\times `Md`=`result` `unit`$",
        r"rho=As/(b*ho)[-1]=  ,per[100]>? rhom= ,per": r"""
    \begin{align*}
    \rho=\frac{\As}{b \ho}=\frac{`As`}{`b`\times `ho`}=0.81913\%\leq \rhom=`rhom`\%
    \end{align*}""",
        r"M=,kNm": r"$M=`M`\kNm$"
    }

    ttp_tmp = r"""
<group name="assign_numeric">
{{ var }}{{ eq | re("\s*=\s*") | strip(' ') }}{{ value | re("[\d\.]+") }}{{ unit | re("(\s+[^\s^,]+)*") | strip(' ') }}{{ comma | re("(\s*,\s*)*") | strip(' ') }}{{ command | re("(\"(.*)\")*") | strip(' "') }}
</group>

<group name="assign_str">
{{ var }}{{ eq | re("\s*=\s*") | strip(' ') }}{{ value | re("\"(.*)\"") | strip('"') }}
</group>

<group name="unit">
unit {{ name | re("[^=]+") }}{{ eq | re("(\s*=\s*)*") | strip(' ') }}{{ command | re("(\".*\")*") | strip(' "') }}
</group>
"""

    latex_tmpl = mapping.get(equation.strip())
    if not latex_tmpl:
        sys.stderr.write("I can't parse it")
        exit(-1)

    category = ttp_process_ds(ds, ttp_tmp)
    ds_var_value = {stmt['var']: stmt['value'] for stmt in category['assign_numeric'] + category['assign_str']}
    latex_code = exp_env.from_string(latex_tmpl).render(**ds_var_value)
    result = json.dumps({
        'result': latex_code,
    }, indent=4, ensure_ascii=False)
    if output_file:
        with open(output_file, 'w+', encoding='utf8') as f:
            f.write(result)
    else:
        print(result)

    return 0
