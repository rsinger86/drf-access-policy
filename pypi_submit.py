import os

os.system("rm dist/*")
os.system("python setup.py sdist --verbose")
os.system("twine upload dist/*")
