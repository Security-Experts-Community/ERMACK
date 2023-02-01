"""Script for creation folders' layout of entities"""

import argparse
import glob
import os
import shutil
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Script for creation entity folder structure"
)

parser.add_argument("-P", "--path", required=True, help="Path to entities folder")
args = parser.parse_args()
path = Path(args.path)

e_list = [
    Path(file)._parts[-1].split(".yml")[0] for file in glob.glob(f"{args.path}/*.yml")
]

for e in e_list:
    os.makedirs(name=(path / e), exist_ok=True)
    shutil.move(src=f"{path}/{e}.yml", dst=f"{path}/{e}/{e}.yml")
