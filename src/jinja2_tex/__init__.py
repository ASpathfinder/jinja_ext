from jinja2 import Environment, select_autoescape, FileSystemLoader, ChoiceLoader, PackageLoader
from jinja2.ext import SwitchStatementExtension, MathExtension
from jinja2_tex.global_function import exp_env
from ttp import ttp
import json
import sys
import os
import re


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
        extensions=[SwitchStatementExtension, MathExtension],
        **kwargs,
    )

    from . global_function import global_function_mapping
    from . filter import calc, calc_equation

    # tex_env.code_generator_class = ExCodeGenerator
    tex_env.globals = global_function_mapping
    tex_env.filters['calc'] = calc
    tex_env.filters['calc_equation'] = calc_equation

    return tex_env


def ttp_pre_process(src_path, template_path):
    order = [
        'var',
        'op1',
        'equation',
        'op2',
        'comma',
        'unit',
        'math_block',
        'math_endblock',
    ]

    convert_mapping = {
        'var': r'{{ process("`ts`") }}',
        'var_2': r'{{ process("`ts`") }}',
        'var_with_unit': r'{{ process("`ts`") }}',
        'equations': r'{{ process("`ts`") }}',
        'math_block': r'{% raw %}{% math %}{% endraw %}',
        'math_endblock': r'{% raw %}{% endmath %}{% endraw %}'
    }
    # with open(template_path, encoding='utf8') as f:
    #     template = f.read()
    #     print(template)

    replacement_mapping = {}

    with open('test/templates/3-18.tmpl', encoding='utf8') as f:
        for line in f.readlines():
            found = re.findall(r'(<.*?>)', line)
            if found:
                for tag in found:
                    parser = ttp(data=tag, template=template_path)
                    parser.parse()
                    results = json.loads(parser.result(format='json')[0])
                    print(tag)
                    # print(results)
                    for match in results:
                        for t in ["var", 'var_2', 'var_with_unit', 'equations', 'math_block', 'math_endblock']:
                            match_dict = match.get(t, None)
                            if match_dict:
                                ordered_keys = sorted(match_dict.keys(), key=lambda k: order.index(k))
                                ordered_match_dict = {key: match_dict.get(key) for key in ordered_keys}
                                ts_key = ''.join(ordered_match_dict.values())
                                replacement_mapping['<{}>'.format(ts_key)] = exp_env.from_string(convert_mapping.get(t)).render(ts=ts_key)

    print(json.dumps(replacement_mapping, indent=4, ensure_ascii=False))

    with open('test/templates/3-18.tmpl', encoding='utf8') as f:
        body = f.read()
        print(body)
        for k, v in replacement_mapping.items():
            print(k, v)
            body = body.replace(k, v)

    with open('test/output/3-18.tmpl.jinja2', 'w+', encoding='utf8') as f:
        f.write(body)


def ttp_process_ds(src_path, template_path):

    with open(src_path, encoding='utf8') as f:
        for line in f.readlines():
            parser = ttp(data=line, template=template_path)
            parser.parse()
            results = json.loads(parser.result(format='json')[0])

        return results
