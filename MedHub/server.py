import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask, request, jsonify, render_template
from Data_Scraping.disease_match_query import *
from Data_Scraping.nearest_doctors.getNearestDoctors import *
import re



app = Flask(__name__)


@app.route('/')
def search():
    return render_template('search_and_results.html')

@app.route('/diseases', methods = ['POST'])
def get_symptoms():
    symptoms = request.form["symptoms"]
    write_query(symptoms)

    out = []

    for disease_file, specialty, prob in disease_match():
        disease_name = disease_file.split('.')[0]
        with open('Data_Scraping/diseases_data/medline/%s' % disease_file, mode='r') as disease_file:
            disease_text = disease_file.read()

        try:
            short_desc_list = disease_text.split('To use the sharing features on this page, please enable JavaScript.')[-1]
            short_desc_list = short_desc_list.replace('\n', '').strip().split('.')[0:3]
            short_desc = '. '.join(short_desc_list) + '...'
        except:
            short_desc = "No description found"

        out.append((disease_name, short_desc, prob, specialty))

    return render_template('search_and_results.html', result= out, text = symptoms)

# @app.route('/diseases/desc/<disease_name>')
# def get_disease_desc(disease_name):
#     return

@app.route('/doctors', methods = ['POST'])
def doctor_search():
    # specialty_text = ', '.join(list(set(request.form.getlist('specialty_check'))))
    specialty_text = ', '.join(list(set(request.form.getlist('specialty_check'))))
    return render_template('doctor_search_and_results.html', text = specialty_text)

@app.route('/doctors/results', methods = ['GET', 'POST'])
def get_specialties():
    specialties = request.form['specialties'].split(', ')
    address = request.form['address']
    num_doctors = int(request.form['num_doctors'])
    max_dist = float(request.form['max_dist'])
    # specialties = [specialty.encode('utf8') for specialty in list(set(request.form.getlist('specialty_check')))]
    print specialties
    doctor_list = getNearestDoctors(addr=address, specialty=specialties, n=num_doctors, max_dist=max_dist)
    print doctor_list
    return render_template('doctor_search_and_results.html', result = doctor_list, text = ', '.join(specialties))


@app.route('/diseases/<symptoms>')
def get_resource_symptoms(symptoms):
    user = request.args.get('user')
    out = dict()
    if user:
        out['user'] = user
    out['symptoms'] = symptoms
    write_query(symptoms)
    out['diseases'] = disease_match()
    return jsonify(out)


if __name__ == "__main__":
    # app.debug = True # only have this on for debugging!
    app.run(host='0.0.0.0') # need this to access from the outside world!
