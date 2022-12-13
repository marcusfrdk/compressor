import math
import os
from argparse import ArgumentParser
from PIL import Image

class Color:
    def __init__(self):
        is_windows = os.name == "nt"
        self.red = "\033[31m" if not is_windows else ""
        self.green = "\033[32m" if not is_windows else ""
        self.end = "\033[0m" if not is_windows else ""

color = Color()

def get_args():
    parser = ArgumentParser()
    parser.add_argument("path", nargs="?", default=os.getcwd(), help="path to file or directory")
    parser.add_argument("-q", "--quality", default=75, type=int, help="quality to compress with")
    parser.add_argument("-r", "--replace", action="store_true", help="replace existing file")
    parser.add_argument("-m", "--method", default=2, type=int, choices=[0, 1, 2, 3], help="method to compress with")
    parser.add_argument("-rm", "--remove", action="store_true", help="delete all files containing '-min' in its name")
    args = vars(parser.parse_args())
    if not os.path.exists(args["path"]):
        raise ValueError(f"File with path '{args['path']}' does not exist.")
    return args

def add_prefix(bytes: str) -> str:
    if bytes == 0:
       return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(bytes, 1024)))
    p = math.pow(1024, i)
    s = round(bytes / p, 2)
    return f"{s}{size_name[i]}"

def compress(path: str, quality: int, replace: bool, method: int = 2):
    assert isinstance(path, str)
    assert isinstance(quality, int)
    assert quality in range(1, 100)

    file_name = os.path.basename(path)
    base_path = os.path.abspath(os.path.dirname(path))
    ext = file_name.split(".")[-1]
    name = file_name.replace(f".{ext}", "") + "-min" if not replace else ""

    fp = os.path.join(base_path, f"{name}.{ext}")
    fpt = os.path.join(base_path, f"{name}-tmp.{ext}")

    img_org = Image.open(path)
    img_opt = img_org.quantize(method=method)

    img_opt.save(fpt, format="PNG", quality=quality)

    size_org = os.stat(path).st_size
    size_opt = os.stat(fpt).st_size
    os.remove(fpt)

    if size_org < size_opt:
        print(f"Failed to compress '{file_name}'")
    else:
        img_opt.save(fp, format="PNG", quality=quality)
        before = color.red + add_prefix(size_org) + color.end
        after = color.green + add_prefix(size_opt) + color.end
        print(f"Compressed file '{file_name}' from {before} to {after}")


def confirm(msg: str) -> bool:
    return input(f"{msg} (y/n): ") in ["y", "yes"]


def is_image(path: str) -> bool:
    exts = ["png", "jpg", "jpeg"]
    return "." in path and path.split(".")[-1] in exts

if __name__ == "__main__":
    args = get_args()

    if is_image(args["path"]):
        compress(args["path"], args["quality"], args["replace"], args["method"])
    else:
        args["path"] = os.path.abspath(args["path"])
        if not os.path.isdir(args["path"]):
            print("Invalid file")
            exit(1)
        if args["remove"]:
            if not confirm(f"The action 'remove' will delete any file that includes '-min' in directory '{args['path']}', continue?"):
                exit(1)
            for file in os.listdir(args["path"]):
                if is_image(file) and "-min" in file:
                    path = os.path.join(args["path"], file)
                    print(f"Removed '{path}'")
                    os.remove(path)
        else:
            for img in [path for path in os.listdir(args["path"]) if is_image(path)]:
                fp = os.path.join(args["path"], img)
                compress(fp, args["quality"], args["replace"], args["method"])