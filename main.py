import math
import os
from argparse import ArgumentParser
from PIL import Image

IMAGE_TYPES = ["png", "jpg", "jpeg", "ico"] # file types the program accepts

class Color:
    """ ASCII Colors (non-windows devices only) """
    def __init__(self):
        is_windows = os.name == "nt"
        self.red = "\033[31m" if not is_windows else ""
        self.green = "\033[32m" if not is_windows else ""
        self.end = "\033[0m" if not is_windows else ""

color = Color()

def get_args() -> dict:
    """ Handles arguments and returns dict """
    parser = ArgumentParser()
    parser.add_argument("path", nargs="?", default=os.getcwd(), help="path to file or directory")
    parser.add_argument("-q", "--quality", default=75, type=int, help="quality to compress with")
    parser.add_argument("-r", "--replace", action="store_true", help="replace existing file")
    parser.add_argument("-m", "--method", default=2, type=int, help="method to compress with", choices=[0, 1, 2, 3])
    parser.add_argument("-rm", "--remove", action="store_true", help="delete all files containing '-min'")
    parser.add_argument("-d", "--dry", action="store_true", help="runs the script without commiting")
    parser.add_argument("-c", "--colors", default=256, type=int, help="sets the number of colors in output image")
    parser.add_argument("-o", "--output", help="sets the name of the output file", type=str)
    args = vars(parser.parse_args())
    if not os.path.exists(args["path"]):
        raise ValueError(f"File with path '{args['path']}' does not exist.")
    if args["colors"] and (args["colors"] < 1 or args["colors"] > 256):
        raise ValueError("Colors must be in range 1-256")
    return args

def add_suffix(bytes: str) -> str:
    """ Adds a file size prefix based on number of bytes """
    value, exp = bytes, 0
    while value >= 1024:
        value /= 1024
        exp += 1
    suffix = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}[exp]
    return str(round(value, 2)) + suffix

def compress(path: str, quality: int, replace: bool, method: int = 2, output_name: str = None, colors: int = 256):
    """ Main compression function """
    assert isinstance(path, str)
    assert isinstance(quality, int)
    assert quality in range(1, 100)
    
    global fails
    fails = 0

    file_name = os.path.basename(path)
    base_path = os.path.abspath(os.path.dirname(path))
    ext = file_name.split(".")[-1]
    name = file_name.replace(f".{ext}", "") + ("-min" if not replace else "") if not output_name else output_name
    tmp_suffix = f"-tmp-{os.urandom(4).hex()}"

    fp = os.path.join(base_path, f"{name}.{ext}")
    fpt = os.path.join(base_path, f"{name}{tmp_suffix}.{ext}")

    img_org = Image.open(path)
    img_opt = img_org.quantize(method=method, colors=colors)

    img_opt.save(fpt, format="PNG", quality=quality)

    size_org = os.stat(path).st_size
    size_opt = os.stat(fpt).st_size
    os.remove(fpt)

    if size_org < size_opt:
        print(f"Failed to compress '{file_name}'")
        fails += 1
    else:
        percent = int((1 - size_opt / size_org) * 100)
        img_opt.save(fp, format="PNG", quality=quality) if not run_dry else None
        before = color.red + add_suffix(size_org) + color.end
        after = color.green + add_suffix(size_opt) + color.end
        new_name = f" -> '{name}.{ext}'" if output_name else ''
        print(f"""Compressed file '{file_name}'{new_name} from {before} to {after} ({percent}%)""")


def confirm(msg: str) -> bool:
    """ Confirm user input """
    return input(f"{msg} (y/n): ") in ["y", "yes"]


def is_image(path: str) -> bool:
    """ Checks if a file is a valid image """
    return "." in path and path.split(".")[-1] in IMAGE_TYPES

if __name__ == "__main__":
    global run_dry
    global fails

    args = get_args()
    run_dry = args["dry"]
    fails = 0

    if args["remove"]:
            if not os.path.isdir(args["path"]):
                print("Path is not a directory.")
                exit(1)
            if not confirm(f"The action 'remove' will delete any file that includes '-min' in directory '{args['path']}', continue?"):
                exit(1)
            for file in os.listdir(args["path"]):
                if is_image(file) and "-min" in file:
                    path = os.path.join(args["path"], file)
                    print(f"Removed '{path}'")
                    os.remove(path)
    else:
        if is_image(args["path"]):
            compress(
                args["path"], 
                args["quality"], 
                args["replace"], 
                args["method"],
                output_name=args["output"],
                colors=args["colors"]
            )
        else:
            args["path"] = os.path.abspath(args["path"])
            if not os.path.isdir(args["path"]):
                print("Invalid file")
                exit(1)
            else:
                if args["output"]:
                    print("Output name only works for single images.")
                for img in [path for path in os.listdir(args["path"]) if is_image(path)]:
                    fp = os.path.join(args["path"], img)
                    compress(fp, args["quality"], args["replace"], args["method"], colors=args["colors"])
                if fails > 0:
                    print(f"{fails} file{'' if fails == 1 else 's'} failed, try switching compression method.")