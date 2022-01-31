from configparser import ConfigParser
from dateutil.relativedelta import relativedelta
import datetime
import requests
import json


def read_config_file():
    cfg = ConfigParser()
    cfg.read(['config.ini',
              '/config/config.ini'])

    return cfg


def main():
    print("Starting document LCM script...\n")

    config = read_config_file()

    global host
    host = config.get('paperless', 'HOST')

    global auth
    auth = requests.auth.HTTPBasicAuth(
        config.get('paperless', 'USER'),
        config.get('paperless', 'PASSWORD'),
    )

    global lcm_prefix
    lcm_prefix = config.get('paperless', 'LCM_PREFIX')

    global auto_delete
    auto_delete = config.getboolean('paperless', 'AUTO_DELETE')

    if not auto_delete:
        removal_tag = config.get('paperless', 'REMOVAL_TAG')
        
        global removal_tag_id
        removal_tag_id = get_removal_tag_id(removal_tag)

    lcm_documents = get_lcm_documents()

    for document in lcm_documents:
        check_document(document)


def get_removal_tag_id(removal_tag):
    response = api_request(f"tags/?name__iexact={removal_tag}")

    return response['results'][0]['id']

def check_document(document):
    print(document['title'])
    for tag in document['tags']:
        tag_name = tag_id_to_name(tag)

        if tag_name.startswith(lcm_prefix):
            document_creation_date = datetime.datetime.strptime(
                document['created'].split('T')[0], '%Y-%m-%d').date()

            lcm_policy = {
                'value': int(tag_name[len(lcm_prefix):-1]),
                'units': tag_name[-1]
            }

            print(f"\tFound LCM tag: {tag_name}")
            print(f"\tDocument creation date: {document_creation_date}")

            today = datetime.date.today()

            if(lcm_policy['units'] == 'd'):
                if today >= document_creation_date + relativedelta(days=lcm_policy['value']):
                    add_removal_tag_or_delete(document['id'])
                else:
                    print(
                        f"\t{((document_creation_date + relativedelta(days=lcm_policy['value'])) - today).days } days to go. ")

            if(tag_name.lower().endswith('m')):
                if today >= document_creation_date + relativedelta(months=lcm_policy['value']):
                    add_removal_tag_or_delete(document['id'])
                else:
                    print(
                        f"\t{ ((document_creation_date + relativedelta(months=lcm_policy['value'])) - today).days } days to go. ")
            if(tag_name.lower().endswith('y')):
                if today >= document_creation_date + relativedelta(years=lcm_policy['value']):
                    add_removal_tag_or_delete(document['id'])
                else:
                    print(
                        f"\t{ ((document_creation_date + relativedelta(years=lcm_policy['value'])) - today).days } days to go. ")

            break


def tag_id_to_name(tag_id):
    tag = api_request(f"tags/{tag_id}/")

    return tag['name']


def get_lcm_documents():
    documents = api_request(f"documents/?tags__name__istartswith={lcm_prefix}")

    return documents['results']


def api_request(url, method='get', body=''):
    if method == 'get':
        response = requests.get(host + '/api/' + url, auth=auth)
    if method == 'put':
        headers = {'Content-type': 'application/json'}
        response = requests.put(host + '/api/' + url,
                                auth=auth, data=body, headers=headers)
    if method == 'delete':
        response = requests.delete(host + '/api/' + url, auth=auth)

    try:
        return response.json()
    except json.JSONDecodeError:
        pass


def add_removal_tag_or_delete(document_id):
    if auto_delete:
        api_request(f"documents/{document_id}/", 'delete')
        print("\t**Document REMOVED**")
    else:
        document = api_request(f"documents/{document_id}/", 'get')
        document['tags'].append(removal_tag_id)

        body = document
        api_request(f"documents/{document_id}/", 'put', json.dumps(document))
        print("\t**Document marked for removal**")


if __name__ == "__main__":
    main()
