import os
import uuid
import shutil


def fix_django_app_label(input_text_data: str):
    """Every django model should have `class: Meta` param with app_label. Replace all of them with """
    by_line = input_text_data.split('\n')
    for index, line in enumerate(by_line):
        if 'app_label' in line:
            by_line[index] = ""
    for index, line in enumerate(by_line):
        if 'class Meta:' in line:
            by_line[index] += f"\n{line.split('class Meta:')[0] * 2}app_label = 'djfake'"
    return "\n".join(by_line)


def detect_orm(input_text_data: str,):
    """Simple detecting ORM by text sample."""
    if 'django' in input_text_data:
        return 'django'
    if 'sqlalchemy' in input_text_data:
        return 'sa'
    raise Exception("Unknown ORM")


def import_user_module(input_text_data: str, safe_mode=False):
    """Save user input file as module and import it in-runtime."""
    if safe_mode:
        raise NotImplementedError("Safe mode still not implemented")
    else:
        print(
            f"Warning: unsafe import! Any code can be execute from your modules till import processing"
        )
    if detect_orm(input_text_data) == 'django':
        input_text_data = fix_django_app_label(input_text_data)
    temp_filename = f"temp_{uuid.uuid4()}"
    try:
        os.mkdir("cache")
    except FileExistsError:
        pass
    with open(f"cache/{temp_filename}.py", "w") as f:
        f.write(input_text_data)
        abspath = os.path.dirname(os.path.abspath(f"{temp_filename}.py"))
    try:
        temp = __import__(f"cache.{temp_filename}")
    except Exception as ex:
        print(ex)
    finally:
        shutil.rmtree(f"{abspath}/cache")
    modules = dir(temp)
    for module in modules:
        if module == temp_filename:
            return getattr(temp, module)
