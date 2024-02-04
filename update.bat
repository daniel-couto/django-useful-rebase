python setup.py sdist
python.exe -m build
twine check dist/*
@REM python.exe -m twine upload --repository testpypi dist/*