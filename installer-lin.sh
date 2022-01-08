# install tkinter: python3-tk
sudo apt-get install python3-tk

python3 -m venv ogr-venv
source ogr-venv/bin/activate
pip install -r requirements.txt
deactivate