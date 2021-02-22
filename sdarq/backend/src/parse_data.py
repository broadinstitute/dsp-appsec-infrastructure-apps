import json

def parse_severities(json_data):
    """
    Returns severities for zap scan
    """
    data = json.dumps(json_data).strip('{}')
    data1 = data.strip(', ').replace(', ','|')
    data2 = data1.strip('[').replace('[','')
    data3 = data2.strip(']').replace(']','')
    data4 = data3.strip('""').replace('"','')
    return data4


def prepare_dojo_input(json_data):
    """
    Returns defect dojo description input
    """
    data = json.dumps(json_data).strip('{}')
    data1 = data.strip(',').replace(',', ' \n')
    data2 = data1.strip('[').replace('[', ' ')
    data3 = data2.strip(']').replace(']', ' ')
    data4 = data3.strip('""').replace('"', ' ')
    return data4