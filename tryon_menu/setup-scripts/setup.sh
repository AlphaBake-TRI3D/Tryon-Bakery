sudo apt install -y python3-pip
sudo apt install -y python3-venv

git clone git@github.com:AlphaBake-TRI3D/Tryon-Bakery.git
cd Tryon-Bakery/tryon_menu/

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic
python manage.py setup_initial_data