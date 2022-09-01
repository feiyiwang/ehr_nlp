import json
import re
import os
import sys
import pandas as pd
from datetime import date
import utility
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))


dir_path = os.path.dirname(os.path.realpath(__file__))

# dir_path = os.path.dirname(os.path.realpath(__file__))
# ptData = [{'id':"Mary Yang","name":"Mary Yang"},{'id':"John Yuehan","name":"John Yuehan"},{'id':"Sadaji V Xyz","name":"Sadaji V Xyz"}]
# with open(dir_path + '/fake_pt_notes.json', 'rb')as ptNotes:
#     noteData = json.load(ptNotes)

statusReg = pd.read_csv('../../Desktop/ehr_nlp/DIED_INFO_STATUS_REGISTRATION_50.csv')
pt_data = statusReg[['PATIENT_ID', 'LAST_NM', 'FIRST_NM', 'MIDDLE_NM', 'BIRTH_DT', 'DEATH_DT', 'LAST_ALIVE_DT',
                     'GENDER_NM', 'DFCI_MRN', 'PRIMARY_PROGRAM_NM']]


def calculate_age(row):
    birth,death = row['BIRTH_DT'].split('-'),row['DEATH_DT'].split('-')
    b = date(int('19'+birth[2]),int(utility.month_dict[birth[1]]),int(birth[0]))
    d = date(int('20'+death[2]),int(utility.month_dict[death[1]]),int(death[0]))
    age = d.year - b.year - ((d.month, d.day) < (b.month, b.day))
    if age > 90:
        return '>90'
    elif age > 80:
        return '80-90'
    elif age > 70:
        return '70-80'
    elif age > 60:
        return '60-70'
    elif age > 50:
        return '50-60'
    else:
        return '0-50'


def calculate_days(row):
    alive,death = row['LAST_ALIVE_DT'].split('-'),row['DEATH_DT'].split('-')
    a = date(int('20'+alive[2]),int(utility.month_dict[alive[1]]),int(alive[0]))
    d = date(int('20'+death[2]),int(utility.month_dict[death[1]]),int(death[0]))
    res = d - a
    return res.days


pt_data['age'] = pt_data.apply(lambda i:calculate_age(i),axis=1)
pt_data['days'] = pt_data.apply(lambda i:calculate_days(i),axis=1)
pt_data = pt_data.rename(columns = {'PRIMARY_PROGRAM_NM':'program'})


program_list = []
for i in pt_data['program'].unique().tolist():
    pl = i.split()
    new_str = ''
    for j in pl:
        new_str += j[0] + j[1:].lower() + ' '
    new_str = new_str.strip()

    program_list.append({'id':i,'name':new_str})


def get_data(opt1, opt2):
    pt_pivot = pd.pivot_table(pt_data, index=[opt1, opt2], aggfunc='count')[['days']]
    pt_pivot_filter = pt_pivot[pt_pivot['days'] > 1]
    data_list = []
    title = ''

    for index, row in pt_pivot_filter.iterrows():
        if title != index[0]:
            if title != '':
                data_list.append(data_dict)
            title = index[0]
            this_title = ' '.join([x[0]+x[1:].lower() for x in title.split()])
            data_dict = {opt1:this_title,'freq':{}}
            for i in pt_pivot_filter.index.get_level_values(opt2).unique().tolist():
                this_i = ' '.join([x[0]+x[1:].lower() for x in i.split()])
                data_dict['freq'][this_i] = 0
        this_index_one = ' '.join([x[0]+x[1:].lower() for x in index[1].split()])
        data_dict['freq'][this_index_one] = row['days']
        if index == pt_pivot_filter.index[len(pt_pivot_filter)-1]:
            data_list.append(data_dict)
    return data_list

# with open(dir_path + "/pt_list.txt", "rb") as ptList:   # Unpickling
#     ptData = pickle.load(ptList)
# with open(dir_path + '/merged_notes.txt', 'rb')as ptNotes:
#     noteData = json.load(ptNotes)

# noteData['4dc32a97-17e1-45b5-b562-49748a62973d']['12345678'] = {u'DateOfService': u'2013-02-01',
#                                                                 u'Group Stage': u'',
#                                                                 u'Identification': u'report number:',
#                                                                 u'Individual Stage': u'',
#                                                                 u'NoteJSON': {u'Date': u'02/28/2013 13:40',
#                                                                              u'Ordering Provider': u'ABC, AABB',
#                                                                              u'Report Number': u'234567',
#                                                                              u'Report Status': u'Final',
#                                                                              u'Reviewed by': u'Wang M.D., Mary. Abnormal ECG When compared with ECG of 01-AUG-2012 02:00. No longer Present Vent. No longer evident in Anterior-lateral leads QT has shortened Confirmed by Wang M.D., Mary. (001) on 3/1/2013 8:00:30 AM',
#                                                                              u'Type': u'12 Lead ECG'},
#                                                                 u'TypeOfService': None}
# noteData['4dc32a97-17e1-45b5-b562-49748a62973d']['87654321'] = {u'DateOfService': u'2012-09-01',
#                                                                  u'Identification': u'conversation',
#                                                                  u'NoteJSON': {u'conversation': u"Yuehan's to treatment was held today as he is currently being treated for UTI.  He rec'd hydration and repeat U/A C+S sent.  Yuehan will RTC in one week for re eval for treatment, he has his f/u appt as well as his team's contact information and agrees to call with questions or concerns."},
#                                                                  u'TypeOfService': u'Progress Notes'}


def get_freetext_list(noteData):
    freetext_set = set()
    for k,v in noteData.items():
        for k1,v1 in v.items():
            note_dict = v1['NoteJSON']
            for k2,v2 in note_dict.items():
                freetext_set.add(k2)
    freetext_list = list(freetext_set)
    return freetext_list


def get_Patient_Notes(patient_id, noteData, cancerData):
    note_dict = noteData[patient_id]
    timeline_notelist = []
    table_notelist = []
    print('get_Patient_Notes')
    for k,v in note_dict.items():
        new_dict = {}
        this_date = re.findall(r'^(\d{4}\-\d{2}\-\d{2})', v['DateOfServiceDTS'])
        if len(this_date) == 1:
            if k in cancerData[patient_id]['notes']:
                results = {}
                for keyword in ['metastasis_key', 'stage_key', 'gleason_key']:
                    if keyword in cancerData[patient_id]['notes'][k]:
                        res = cancerData[patient_id]['notes'][k][keyword]['00']['extract']
                        res = ['metastasis' if j[:3] == 'met' else j for j in res.lower().split(', ')]
                        res = ', '.join(set(res))
                        if isinstance(res, dict) is True:
                            res = res['00'] + '<br>'
                        elif isinstance(res, str) and (res != ''):
                            res = res + '<br>'
                        else:
                            res = ''
                    else:
                        res = ''
                    results[keyword] = res

                if 'Code Status' in v:
                    status = v['Code Status'] + '<br>'
                else:
                    status = ''
            else:
                results, status = {'metastasis_key': '', 'stage_key': '', 'gleason_key': ''}, ''

            new_dict['className'] = 'green'
            new_dict['id'] = k
            new_dict['content'] = results['metastasis_key'] + results['stage_key'] + results['gleason_key'] + status + '<a href="#readTable" onclick="showNoteTable(' + str(k) + ')">Note ID: ' + str(k) + '</a> <a href="#reportModal" data-toggle="modal" data-target="#reportModal" onclick="reportNoteError(' + str(k) + ')" style="color:#bc1e1e;"><i class="glyphicon glyphicon-flag"></i></a>'

            if len(v.keys()) > 3:
                new_dict['group'] = 'Inpatient'
            else:
                new_dict['group'] = 'Outpatient'

            if isinstance(v['InpatientNoteTypeDSC'], str):
                new_dict['subgroup'] = v['InpatientNoteTypeDSC']
                new_dict['title'] = '<b>' + v['InpatientNoteTypeDSC'] + '</b>'
            else:
                if type(v['InpatientNoteTypeDSC']) is float:
                    print("~~~~")
                    print(v['InpatientNoteTypeDSC'])
                    print("~~~~")
                else:
                    print("****")
                    print("****")
                new_dict['subgroup'] = 'No Type'
                new_dict['title'] = '<b>No Type</b>'

            new_dict['start'] = str(v['DateOfServiceDTS']).split(' ')[0]

            timeline_notelist.append(new_dict)

        else:
            new_dict['id'],new_dict['type'],new_dict['content'] = k,v['InpatientNoteTypeDSC'],v['NoteJSON']
            if k in cancerData[patient_id]['notes']:
                if 'metastasis_key' in cancerData[patient_id]['notes'][k]:
                    gstage = cancerData[patient_id]['notes'][k]['metastasis_key']['00']['extract']
                    if isinstance(gstage, dict):
                        gstage = gstage['00'] + '<br>'
                    elif isinstance(gstage, str) and (gstage != ''):
                        gstage = gstage + '<br>'
                    else:
                        gstage = ''
                else:
                    gstage = ''

                if 'Code Status' in v:
                    status = v['Code Status'] + '<br>'
                else:
                    status = ''

                new_dict['keyword'] = gstage + status

                table_notelist.append(new_dict)
    if patient_id == 'patient_id_2':
        timeline_notelist.append({'id': 'Death Date', 'content': 'Death Date: 12/16/2016', 'group': 'Inpatient', 'start': '12/16/2016', 'className':'darkRed'})
    return timeline_notelist, table_notelist


# [{'section': sections[i], 'content': contents[i]},{'section': sections[i], 'content': contents[i]}]
def get_Keywords_Notes(patientId, keywords, noteData, cancerData):
    keywordsInKeys, keywordsInValues = [], []
    if keywords != '':
        thisPtDict = noteData[patientId]
        for k,v in thisPtDict.items():
            section_dict = v['NoteJSON']
            for title,content in section_dict.items():
                title = title
                if isinstance(content, dict):
                    content = str(content)
                content = content
                if keywords in title:
                    keywordsInKeys.append({'date':v['DateOfServiceDTS'],'noteid':k,'title':title,'content':content})
                if keywords in content:
                    keywordsInValues.append({'date':v['DateOfServiceDTS'],'noteid':k,'title':title,'content':content})
    return keywordsInKeys, keywordsInValues

    # matching = [s for s in some_list if "abc" in s]


def get_Note(patient_id,note_id, noteData):
    return noteData[patient_id][note_id]['NoteJSON']


def update_Note(patient_id, note_id, note_fb, person_fb, date_fb, noteData):
    newKey = date_fb + ' ' + person_fb
    try:
        noteData[patient_id][note_id]['Note Comments'][newKey] = note_fb
    except:
        noteData[patient_id][note_id]['Note Comments'] = {}
        noteData[patient_id][note_id]['Note Comments'][newKey] = note_fb
    print(noteData[patient_id][note_id]['Note Comments'][newKey])


def save_file(noteData):
    with open(dir_path + '/fake_pt_notes_update.json', 'w')as ptNotes_update:
        json.dump(noteData, ptNotes_update)

# {'id': 123,'content': 'Full Code<br><a href="#readTable" onclick="showNoteTable(123)">Note ID: 123</a> <a href="" onclick=reportNoteError(123)" style="color:#bc1e1e;"><i class="glyphicon glyphicon-flag"></i></a>'','group': 'Inpatient','start': '2013-04-27', 'title': '<b>Progress Notes</b>', 'className':'darkRed'}
