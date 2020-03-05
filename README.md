# amr-flask

This repository provides a new implementation for Abstract Meaning Representation (AMR) annotation. It uses data from the AMR bank (https://amr.isi.edu/). 

After running the server, users can view, navigate, and annotate sentences using the representation specified here: https://amr.isi.edu/language.html .

How to run development server:  
. venv/bin/activate  
export FLASK_APP=app.py  
export AMR_SETTINGS=settings.cfg  
export FLASK_ENV=development  
flask init-db  
flask run
