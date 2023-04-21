import argparse
import json
import logging
import os
import requests
import sys
import tarfile
import traceback as tb

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s %(levelname)s [%(filename)s:'
                    '%(lineno)d]: %(message)s')

parser = argparse.ArgumentParser()
parser.add_argument(
    "index",
    help="elastic index to upload from archive with same name"
)
parser.add_argument(
    "-d", 
    "--directory",
    type=str,
    required=False,
    help="directory where files are extracted from index archives"
)
parser.add_argument(
    "-o", 
    "--organization",
    type=str,
    required=False,
    help="organization from where index archives are retrieved"
)
args = parser.parse_args()

target_dir = args.directory if args.directory else os.path.join(os.sep, 'tmp')
organization = args.organization if args.organization else 'opencybersecurityalliance'
url = '/'.join([
    'https://api.github.com',
    'repos',
    organization,
    'data-bucket-kestrel',
    'contents',
    'elasticsearch',
    f'{args.index}.tar.gz'
    ])

response = requests.get(url, stream=True)
if response.status_code != 200:
    logging.error(f'{response.status_code} - failed to retrieve metadata fpr'
                  f'{args.index}.tar.gz file: {response.text}')
    sys.exit(-1)
file_info = response.json()
download_url = file_info.get('download_url')
if download_url is None:
    logging.error(f'Could not find download_url in '
                  f'{json.dumps(file_info, indent=2)}')
    sys.exit(-1)

target_path = os.path.join(target_dir, f'{args.index}.tar.gz')
response = requests.get(download_url, stream=True)
if response.status_code != 200:
    logging.error(f'{response.status_code} - failed to retrieve '
                  f'{args.index}.tar.gz file: {response.text}')
    sys.exit(-1)
    
index_archive = tarfile.open(fileobj=response.raw, mode="r|gz")
index_archive.extractall(path=target_dir)
index_archive.close()
mapping_file_name = os.path.join(target_dir, f'{args.index}.mapping.json')
try:
    with open(mapping_file_name, 'r') as fp:
        index_mappings = json.load(fp)
except:
    logging.error(f'Failed to load json mappings from file '
                  f'{mapping_file_name}: {tb.print_exc()}')
    sys.exit(-1)

index_mappings[args.index]['mappings']['properties']['process'][
    'properties']['parent']['properties']['command_line'][
    'fields']['keyword']['ignore_above'] = 1024
index_mappings[args.index]['mappings']['properties']['process'][
    'properties']['command_line']['fields']['keyword']['ignore_above'] = 1024
with open(mapping_file_name, 'w') as fp:
    fp.write(json.dumps(index_mappings))
