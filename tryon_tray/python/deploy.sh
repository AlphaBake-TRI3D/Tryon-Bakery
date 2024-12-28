#fill the ~/.pypirc file with your pypi credentials -> vi /Users/nitish/.pypirc
rm -rf dist/ build/; python -m build
python -m twine upload --repository pypi dist/*

#