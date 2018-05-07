import requests
import os
import argparse
from subprocess import call


def file_key(f):
    if not '-' in f:
        return -1
    else:
        return int(f.split('-')[1].split('.')[0])


def clean_dir(path):
    if os.path.exists(path):
        for filename in os.listdir(path):
            os.remove(path + filename)

    if not os.path.exists(path):
        os.mkdir(path)


def to_ocr(pdf_path, id):
    base_dir = '/tmp/pdf_to_ocr_out_' + str(id) + '/'
    clean_dir(base_dir)

    assert os.path.exists(base_dir)
    assert len(os.listdir(base_dir)) == 0

    image_out = base_dir + 'out.png'
    command = 'convert -density 300 -units PixelsPerInch '\
        + pdf_path + ' -quality 100 ' + image_out
    call(command.split())
    print('image conversion done')

    with open(base_dir + 'png.list', 'w') as png_list:
        files = [f for f in os.listdir(base_dir) if f.endswith('.png')]
        files = sorted(files, key=file_key)
        png_list.write('\n'.join([base_dir + f for f in files]))

    command = 'tesseract ' + base_dir + 'png.list ' + base_dir + 'ocr'
    call(command.split())

    with open(base_dir + 'ocr.txt', 'r') as ocr:
        text = ocr.read()
    print('ocr done')

    clean_dir(base_dir)
    os.removedirs(base_dir)

    return text


def update_document_ocr(id, api_key=None, url=None):
    eqs = '===================================================================='
    print(eqs)
    print('Document', id)
    print(eqs)
    url = url.rstrip('/') + '/api/'
    req = requests.get(url + 'files/' + str(id))
    if len(req.content) > 50000:
        return
    item = req.json()
    if 'message' in item and item['message'].endswith('Record not found.'):
        print('Record with id ' + str(id) + ' could not be found.')
        return
    print('file retrieved')

    pdf_path = '/tmp/ocr_pdf_out_' + str(id) + '.pdf'
    if 'file_urls' in item:
        pdf = requests.get(item['file_urls']['original'])
        with open(pdf_path, 'wb') as out:
            out.write(pdf.content)
            print('pdf written')

    ocr_text = to_ocr(pdf_path, id)

    os.remove(pdf_path)

    req = requests.get(url + 'items/' + str(id))
    item = req.json()
    print('item retrieved')

    if not 'element_texts' in item:
        return
    for i, element_text in enumerate(item['element_texts']):
        if element_text['element']['name'] == 'Text' \
                and element_text['element_set']['name'] == 'Item Type Metadata':
            item['element_texts'][i]['text'] = ocr_text
            break
    else:
        print('Could not find Text element for document ' + str(id))
        print('Generating Text element from scratch.')
        item['element_texts'].append({
            'html': False,
            'text': ocr_text,
            'element_set': {
                'id': 3,
                'url': url + 'element_sets/3',
                'name': 'Item Type Metadata',
                'resource': 'element_sets'
            },
            'element': {
                'id': 1,
                'url': url + 'elements/1',
                'name': 'Text',
                'resource': 'elements'
            }
        })

    req = requests.put(url + 'items/' + str(id) + '?key=' + api_key, json=item)
    print('update request sent')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run OCR on a set of Omeka pdfs.'
    )
    parser.add_argument('url', help='Base URL for the Omeka instance')
    parser.add_argument('key', help='API key for the Omeka instance')
    parser.add_argument('-s', '--start',
                        help='Document ID where OCR should begin',
                        type=int, default=0)
    parser.add_argument('-e', '--end',
                        help='Document ID where OCR should end',
                        type=int, default=100000)

    args = parser.parse_args()
    for i in range(args.start, args.end):
        update_document_ocr(i, url=args.url, api_key=args.key)
