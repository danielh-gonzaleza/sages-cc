import requests
import xml.etree.ElementTree as ET
import csv
import chardet

from variables import blacklisted_prepositions




def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)  # Read a small part of the file
        result = chardet.detect(raw_data)
    return result['encoding']


def detect_delimiter(file_path, encoding):
    with open(file_path, 'r', encoding=encoding) as f:
        sample = f.read(1024)  # Read a sample to detect the delimiter
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter


def remove_blacklist_prepositions(names_list: list) -> list:
    return list(set(names_list) - set(blacklisted_prepositions))


def load_un_sanction_names_xml(url: str) -> list:

    sanctioned_list = []

    response = requests.get(url)
    if response.status_code == 200:
        xml_data = response.content
        root = ET.fromstring(xml_data)

        for individual in root.findall(".//INDIVIDUAL"):
            individual_dict = {"DATAID": individual.findtext("DATAID")}

            name = ""
            names_list = []

            for element in individual:
                if "_NAME" in element.tag:
                    name += element.text + " "
                    if " " in element.text:
                        names_list += element.text.split(" ")
                    else:
                        names_list.append(element.text)

            individual_dict["NAMES"] = name.strip()
            individual_dict["NAME_LIST"] = names_list

            sanctioned_list.append(individual_dict)
    else:
        print("Failed to download XML:", response.status_code)

    return sanctioned_list


def load_clients_csv(csv_file_path: str) -> list:

    client_list = []
    duplicate_control = []

    encoding = detect_encoding(csv_file_path)

    delimiter = detect_delimiter(csv_file_path, encoding)

    with open(csv_file_path, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)

        for row in reader:
            document_id = row["CEDULA"].strip()
            names = row["NOMBRE"].strip()

            if document_id not in duplicate_control:

                duplicate_control.append(document_id)

                names = names.replace(",", "")
                names = names.replace(".", "")
                names_list = names.split()

                client_list.append({
                    "CEDULA": document_id,
                    "NAMES": names,
                    "NAME_LIST": names_list
                })

    return client_list


def validate_client_list(client_csv_file_path: str, un_sc_url: str, number_of_matches: int):

    client_list = load_clients_csv(client_csv_file_path)

    sanctioned_list = load_un_sanction_names_xml(un_sc_url)

    matched_clients = []

    for client in client_list:

        client_names = remove_blacklist_prepositions(client['NAME_LIST'])

        for sanctioned in sanctioned_list:

            sanctioned_names = remove_blacklist_prepositions(sanctioned['NAME_LIST'])

            matching_names = list(set(client_names) & set(sanctioned_names))

            if len(matching_names) >= number_of_matches:
                matched_clients.append({
                    "CEDULA": client["CEDULA"],
                    "NOMBRE_CLIENTE": client["NAMES"],
                    "DATAID": sanctioned["DATAID"],
                    "NOMBRE_UN": sanctioned['NAMES'],
                    "COINCIDENCIAS": matching_names
                })

    return matched_clients