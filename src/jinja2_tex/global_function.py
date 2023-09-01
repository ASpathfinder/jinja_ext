from jinja2 import Environment

exp_env = Environment(trim_blocks=True,
                      lstrip_blocks=True,
                      variable_start_string='`',
                      variable_end_string='`'
                      )


def convert(exp, **kwargs):
    return exp_env.from_string(exp).render(**kwargs)


def process(ts):
    return 'processed_ts'


global_function_mapping = {
    'convert': convert,
    'process': process,
}
