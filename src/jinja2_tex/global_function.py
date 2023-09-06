from jinja2 import Environment, pass_environment
import subprocess
import json


exp_env = Environment(trim_blocks=True,
                      lstrip_blocks=True,
                      variable_start_string='`',
                      variable_end_string='`'
                      )


def convert(exp, **kwargs):
    return exp_env.from_string(exp).render(**kwargs)


@pass_environment
def process_equation(env, ts):
    command = ["texsh.exe", "--ds", env.ds_file_path, "-e", "{}".format(ts)]
    complete = subprocess.run(command, capture_output=True)
    try:
        complete.check_returncode()
    except subprocess.CalledProcessError as e:
        result = {
            'error': True,
            'result': "<{}>".format(ts),
        }
    else:
        try:
            result = json.loads(complete.stdout.decode())
        except json.JSONDecodeError as e:
            return  {
            'error': True,
            'result': str(e),
        }

    return result


global_function_mapping = {
    'convert': convert,
    'process_equation': process_equation,
}
