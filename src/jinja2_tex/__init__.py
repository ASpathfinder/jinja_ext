from jinja2 import Environment, select_autoescape, FileSystemLoader, ChoiceLoader, PackageLoader
from jinja2.ext import SwitchStatementExtension
import sys
import os


def create_tex_env(*args, template_folder, **kwargs):
    tex_env = Environment(
        *args,
        loader=ChoiceLoader([
            FileSystemLoader(os.path.join(os.environ.get('PYTHONPATH', ''), 'templates')),
            FileSystemLoader('templates'),
            FileSystemLoader(template_folder),
        ]),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        extensions=[SwitchStatementExtension],
        **kwargs,
    )

    from . global_function import global_function_mapping
    from . filter import calc, calc_equation

    # tex_env.code_generator_class = ExCodeGenerator
    tex_env.globals = global_function_mapping
    tex_env.filters['calc'] = calc
    tex_env.filters['calc_equation'] = calc_equation

    return tex_env




