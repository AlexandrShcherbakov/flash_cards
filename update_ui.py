import glob
import os

for file in glob.glob("*.ui"):
  filename = file.rsplit(".", 1)[0]
  os.system(f"pyside6-uic.exe {file} -o ui_{filename}.py")
