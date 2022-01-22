import argparse
import os

from app import App
from core.const import SUPPORTED_ORMS


def cli():
    parser = argparse.ArgumentParser(description="ORM Combine")
    parser.add_argument(
        "--input", "-i", type=str, help="Input file with models to convert"
    )
    parser.add_argument(
        "--to",
        "-t",
        type=str,
        help=f"Output ORM name (one of :{[i for i in SUPPORTED_ORMS]}",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="output.py",
        help="Output file name",
        required=False,
    )

    args = parser.parse_args()
    input_file = args.input
    to_orm = args.to

    output_file = args.output

    if not output_file.endswith("py"):
        output_file += ".py"

    app = App()
    with open(f"{input_file}") as input_file_reader:
        raw_text = input_file_reader.read()
    result = app.process(raw_text, to_orm)
    with open(f"{output_file}", "w") as f:
        f.write(result)
    os.system(f"python -m black {output_file}")


if __name__ == "__main__":
    cli()
