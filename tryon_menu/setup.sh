sudo apt install -y python3-pip
sudo apt install -y python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py setup_initial_data