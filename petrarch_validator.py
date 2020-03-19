import csv
import json
from statistics import mean
import pandas as pd
import requests
from similarity_finder import get_similarity_using_spacy

headers = {'Content-Type': 'application/json'}

def preprocess_data_remove_unannotated_data():
    fields = ['eventid', 'attacktype1_txt', 'targtype1_txt', 'gname', 'weaptype1_txt', 'summary']
    data = pd.read_csv('data/globalterrorismdb_0718dist.csv', encoding='iso-8859-1', usecols=fields)
    data = data.dropna()
    data.summary = data.summary.str.split(':').str[1]
    data.to_csv('data/pregtd.csv')


def get_details_from_preprocessed_file(input_file):
    df = pd.read_csv(input_file)
    return df


def get_event_details_from_data_frame(df):
    event_id = df[df.columns[1]]
    summary = df[df.columns[2]]
    human_annotated_action = df[df.columns[3]]
    human_annotated_target = df[df.columns[4]]
    human_annotated_source = df[df.columns[5]]
    return event_id, summary, human_annotated_source, human_annotated_action, human_annotated_target


def hit_hypnos(event_id, date, summary):
    data = {
        'text': summary,
        'id': str(event_id),
        'date': date}
    data = json.dumps(data)
    response = requests.get('http://localhost:5002/hypnos/extract', data=data, headers=headers)
    response_data = response.json()
    event_data = response_data.get(str(event_id))
    if event_data is None:
        return None
    sents_data = event_data.get('sents')
    return sents_data


def extract_sat(sent_data):
    meta = sent_data.get('meta')
    if meta is None:
        return None, None, None
    source_target_list = meta.get('actortext')
    action_list = meta.get('eventtext')
    if source_target_list is None or action_list is None:
        return None, None, None

    source_target1 = source_target_list[0]
    if source_target1 is None or len(source_target1) <= 0:
        return None, None, None
    source = source_target1[0]
    target = source_target1[1]
    action = action_list[0]

    return source, action, target


def ignore_not_captured_event_and_dummy_score(human_annotated_source, human_annotated_action, human_annotated_target,
                                              petrarch2_extracted_source, petrarch2_extracted_action,
                                              petrarch2_extracted_target):
    if petrarch2_extracted_source is None or petrarch2_extracted_action is None or petrarch2_extracted_target is None:
        return None

    similarity_score = 1
    return similarity_score


def write_event_details_to_file(filename, event_id, summary, human_annotated_source, human_annotated_action,
                                human_annotated_target, petrarch2_extracted_source, petrarch2_extracted_action,
                                petrarch2_extracted_target, similarity_score, i):
    with open(filename, 'a') as csvfile:
        output_writer = csv.writer(csvfile)
        output_writer.writerow((event_id, summary, human_annotated_source, human_annotated_action,
                                human_annotated_target, petrarch2_extracted_source, petrarch2_extracted_action,
                                petrarch2_extracted_target, similarity_score))
    print('Appended file ' + str(i))


def read_summary_hit_hypno_write_output_to_partial_output(event_id_list, summary_list, human_annotated_source_list,
                                                          human_annotated_action_list, human_annotated_target_list):
    for i in range(len(event_id_list)):
        event_id = event_id_list[i]
        summary = summary_list[i]
        human_annotated_source = human_annotated_source_list[i]
        human_annotated_action = human_annotated_action_list[i]
        human_annotated_target = human_annotated_target_list[i]
        petrarch2_extracted_source, petrarch2_extracted_action, petrarch2_extracted_target = None, None, None
        sents_data = hit_hypnos(event_id, '20191212', summary)
        if sents_data is None:
            write_event_details_to_file(event_id, summary, human_annotated_source, human_annotated_action,
                                        human_annotated_target, petrarch2_extracted_source, petrarch2_extracted_action,
                                        petrarch2_extracted_target, None, i)
            continue
        for key in sents_data.keys():
            petrarch2_extracted_source, petrarch2_extracted_action, petrarch2_extracted_target = extract_sat(
                sents_data.get(key))
            if petrarch2_extracted_source is not None and petrarch2_extracted_action is not None and petrarch2_extracted_target is not None:
                break

        similarity_score = ignore_not_captured_event_and_dummy_score(human_annotated_source, human_annotated_action,
                                                                     human_annotated_target, petrarch2_extracted_source,
                                                                     petrarch2_extracted_action,
                                                                     petrarch2_extracted_target)
        write_event_details_to_file('data/partial_output.csv', event_id, summary, human_annotated_source,
                                    human_annotated_action, human_annotated_target, petrarch2_extracted_source,
                                    petrarch2_extracted_action, petrarch2_extracted_target, similarity_score, i)


def read_partial_output_and_remove_events_not_detected_petrarch(partial_output_file):
    df = pd.read_csv(partial_output_file)
    df = df.dropna()
    df.to_csv("data/similarity_file.csv")


def get_similarity_score(human_annotated_source, human_annotated_action, human_annotated_target,
                         petrarch2_extracted_source, petrarch2_extracted_action, petrarch2_extracted_target):
    similarity_source = get_similarity_using_spacy(human_annotated_source, petrarch2_extracted_source)
    similarity_action = get_similarity_using_spacy(human_annotated_action, petrarch2_extracted_action)
    similarity_target = get_similarity_using_spacy(human_annotated_target, petrarch2_extracted_target)

    similarity_score = mean([similarity_source, similarity_action, similarity_target])
    return similarity_score


def read_similarity_file_update_similarity_values_spacy(similarity_file):
    df = pd.read_csv(similarity_file)
    event_id_list = df[df.columns[1]]
    summary_list = df[df.columns[2]]
    human_annotated_source_list = df[df.columns[3]]
    human_annotated_action_list = df[df.columns[4]]
    human_annotated_target_list = df[df.columns[5]]
    petrarch2_extracted_source_list = df[df.columns[6]]
    petrarch2_extracted_action_list = df[df.columns[7]]
    petrarch2_extracted_target_list = df[df.columns[8]]

    for i in range(len(event_id_list)):
        event_id = event_id_list[i]
        summary = summary_list[i]
        human_annotated_source = human_annotated_source_list[i]
        human_annotated_action = human_annotated_action_list[i]
        human_annotated_target = human_annotated_target_list[i]
        petrarch2_extracted_source = petrarch2_extracted_source_list[i]
        petrarch2_extracted_action = petrarch2_extracted_action_list[i]
        petrarch2_extracted_target = petrarch2_extracted_target_list[i]
        similarity_score = get_similarity_score(human_annotated_source, human_annotated_action, human_annotated_target,
                                                petrarch2_extracted_source, petrarch2_extracted_action,
                                                petrarch2_extracted_target)
        write_event_details_to_file('data/final.csv', event_id, summary, human_annotated_source, human_annotated_action,
                                    human_annotated_target, petrarch2_extracted_source, petrarch2_extracted_action,
                                    petrarch2_extracted_target, similarity_score, i)


if __name__ == '__main__':
    preprocess_data_remove_unannotated_data()
    df = get_details_from_preprocessed_file('data/pregtd.csv')
    event_id, summary, human_annotated_source, human_annotated_action, human_annotated_target = get_event_details_from_data_frame(
        df)
    read_summary_hit_hypno_write_output_to_partial_output(event_id, summary, human_annotated_source,
                                                          human_annotated_action, human_annotated_target)
    read_partial_output_and_remove_events_not_detected_petrarch("data/partial_output.csv")
    read_similarity_file_update_similarity_values_spacy("data/similarity_file.csv")
