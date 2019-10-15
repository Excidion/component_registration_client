if [ -z "$1" ]; then
    echo 'No argument for kernel name supplied.'
    return
fi
python3.7 -m venv ../ENV
source ../ENV/bin/activate
pip install --upgrade pip
pip install jupyter
python -m ipykernel install --user --name $1 --display-name "Python 3.7 ($1)"
pip install -r requirements.txt
jupyter kernelspec list
python --version
