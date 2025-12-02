CSB Project 1 – Vulnerable Django Web Application

This project is a deliberately vulnerable Django web application

The vulnerable code can be found inside the vulnsite/core directory.  
Each vulnerability is implemented intentionally, with screenshots and explanations included in the repository.

Installation and Usage Instructions

1. Clone the repository

git clone https://github.com/Jouni031002/CSB-project-1.git

cd CSB-project-1/vulnsite

2. Create and activate virtual environment (Optional)

python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

3. Install dependencies

pip install -r requirements.txt

If you reveive an error about missing packages like dotenv or requests, use:

pip install python-dotenv requests

4. Create a .env file

In the vulnsite directory, create a file named .env:

SECRET_KEY=changeme
DEBUG=True

You can generate a secure key using Python:

run:
python manage.py shell

import secrets

secrets.token_hex(32)

5. Set up the database

rm db.sqlite3  # optional, if file exists

python manage.py migrate

6. Load sample data

run:

python sample_data.py


7. Run the dev server

python manage.py runserver

The server is now running at http://localhost:8000/