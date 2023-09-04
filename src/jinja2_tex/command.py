from . import create_tex_env, ttp_process_ds
import click
import os


@click.command('parse')
@click.option('--template', '-t', help='模板文件路径')
@click.option('--output-dir', '-o', help='输出目录')
def render_tex(template, output_dir):
    if not os.path.exists(template):
        print("模板文件 '{}' 不存在".format(template))
        exit(-1)

    os.makedirs(output_dir, exist_ok=True)

    abs_path = os.path.abspath(template)
    head, file_name = os.path.split(abs_path)

    tex_env = create_tex_env(template_folder=head)

    # 读取用户自定义 tex 模板，并加入系统预定义的模板内容
    #with open(abs_path, 'r') as f:
    #    tmpl_string = tex_env.get_template('prepare.jinja2').render(user_raw=f.read())

    # 渲染上一步处理过的用户模板
    #template_obj = tex_env.from_string(tmpl_string)
    template_obj = tex_env.get_template(file_name)

    with open(os.path.join(output_dir, file_name), 'w+', encoding='utf8') as f:
        f.write(template_obj.render())


@click.command('texsh')
@click.option('--ds', help='ds 文件路径')
@click.option('--equation', '-e', default=None, help='输入公式')
@click.option('--output-file', '-o', default=None, help='计算结果输出文件路径，不指定则输出到标准输出')
def tex_sh(ds, equation, output_file):
    ttp_process_ds(ds, 'test/ttp/ds.xml')
    # {
    #     "b*h==": r"$b\times h={}\mm\times 500\mm$"
    # }
    return 0


