from flask import Flask, request, jsonify
import data_process
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
# import datefinder
import json

app = Flask(__name__, static_url_path='')

session_dict = {'is_data_processed': False}
noteData = json.load(open('test_dict.json', 'rb'))
cancerData = json.load(open('test_scores_dict.json', 'rb'))
ptData = noteData.keys()


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route("/getPatientList", methods=["GET"])
def get_patient_list():
    return jsonify(patient_list = [{'id':pt} for pt in ptData])


@app.route("/getFreetextList", methods=["GET"])
def get_freetext_list():
    info = data_process.get_freetext_list(noteData)
    return jsonify(freetext_list=info)


@app.route("/getPatientNotes", methods=["GET"])
def get_patient_notes():
    patientId = request.args.get('patientId')
    keywords = request.args.get('keywords')
    timeline_notes, table_notes = data_process.get_Patient_Notes(patientId, noteData, cancerData)
    keywordsInKeys, keywordsInValues = data_process.get_Keywords_Notes(patientId, keywords, noteData, cancerData)
    return jsonify(patientId=patientId, timeline_notes=timeline_notes, table_notes=table_notes,
                   keywordsInKeys=keywordsInKeys, keywordsInValues=keywordsInValues)


@app.route("/getNote", methods=["GET"])
def get_note():
    patient_id = request.args.get('patient_id')
    note_id = request.args.get('note_id')
    note = data_process.get_Note(patient_id, note_id, noteData)
    return jsonify(note=note)


@app.route("/getReportBox", methods=["GET"])
def get_report_box():
    try:
        patient_id = request.args.get('patient_id')
        note_id = request.args.get('note_id')
        note = data_process.get_Note(patient_id, note_id)
        return jsonify(note = note)
    except Exception as e:
        print(e)
        return jsonify(note = {'error':'Please type in a correct NoteID.'})


@app.route("/updateNote", methods=["POST"])
def update_note():
    parameters = request.get_json()
    #print(incoming["patient_id"])
    patient_id = parameters['patient_id']
    note_id = parameters['note_id']
    note_fb = parameters['note_fb']
    person_fb = parameters['person_fb']
    date_fb = parameters['date_fb']

    try:
        data_process.update_Note(patient_id, note_id, note_fb, person_fb, date_fb, noteData)
        message = 'Successfully updated!'
    except Exception as e:
        message = 'Failed! Reason: ' + str(e)

    return jsonify(message = message)


@app.route("/getProgramList", methods=["GET"])
def get_program_list():
    return jsonify(pg_list=data_process.program_list)


@app.route("/getDashboard", methods=["POST"])
def get_data_for_dashboard():
    parameters = request.get_json()
    opt1 = str(parameters['opt1'])
    opt2 = str(parameters['opt2'])
    message = data_process.get_data(opt1, opt2)
    return jsonify(message=message)


# @app.route("/loadFile", methods=["GET"])
# def load_file():
#     try:
#         message = 'Successfully loaded!'
#     except Exception as e:
#         message = str(e)
#     return jsonify(message = message)

# @app.route("/saveFile", methods=["GET"])
# def save_file():
#     try:
#         data_process.save_file
#         message = 'Successfully saved!'
#     except Exception as e:
#         message = str(e)
#     return jsonify(message = message)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=False, host='localhost', port=5050)


