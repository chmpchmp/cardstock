# generates multiple webpages based on template.html

import urllib.request, urllib.parse, urllib.error
import json
import pathlib


class MissingSetError(Exception):
    pass


ENABLE_LINK_GENERATION = True


def run():
    SETLIST = []

    path = pathlib.Path('webpage/card')
    if not path.exists(): path.mkdir()

    if SETLIST == []:
        # adds all existing set codes SETLIST
        data = access_data('https://api.scryfall.com/sets')

        for set in data['data']:
            SETLIST.append(set['code'])
        
        start_set = ''

        if start_set != '':
            index = SETLIST.index(start_set)

            SETLIST = SETLIST[index:]

    count = 0
            
    for set in SETLIST:

        print('Detected set code:', set)

        api_address_extension = '/sets/' + set.lower()
        url = 'https://api.scryfall.com' + api_address_extension

        print('    Creating API URL...', url)

        set_data = access_data(url)

        if set_data == None: raise MissingSetError(set)

        set_search_uri = set_data['search_uri']

        print('    Current set:', set_data['name'])
        print('    Accessing API data...')
        print()

        card_data = access_data(set_search_uri)

        if card_data != None:
            process_webpage(card_data)

            # accesses the next page of the API if it exists
            while card_data['has_more']:
                search_uri = card_data['next_page']
                card_data = access_data(search_uri)
                process_webpage(card_data)

        count += 1
        print('    ' + str(count) + ' out of ' + str(len(SETLIST)) + ' sets completed, ' + str(round((count / len(SETLIST)) * 100, 2)) + ' percent complete')
        print()

    print('Generation complete!')
    print()


def process_webpage(card_data: dict) -> None:
    '''
    Uses card data dictionary to create multiple webpages
    '''
    for card in card_data['data']:
        if 'tcgplayer_id' in card.keys() and card['digital'] == False:   # ensures that a physical version of the card exists
            # file name creation
            file_name = create_file_name(card)

            # reading in the template
            data = open_template('template/card/m10/146/template.html')

            # replacing template variables
            data = replace_data(data, card)

            # directory of output webpages
            directory = 'webpage/card/' + card['set'] + '/' + card['collector_number'] + '/'
            generate_webpage(directory, file_name, data)


def access_data(url: str) -> dict:
    '''
    Returns a dictionary of data of the cards that satisfy
    the search query parameters
    '''
    try:
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)

        try:
            return json.load(response)
        finally:
            response.close()
    except urllib.error.HTTPError as exception:
        pass


def create_file_name(card: dict) -> str:
    '''
    Creates a name for the html file
    '''
    language = card['lang']
    collector_number = card['collector_number']
    set_code = card['set']
    scryfall_uri = card['scryfall_uri']

    # the only non-english language fully supported in the file names is japanese
    #
    # comes from secret lair japanese cards

    if 'printed_name' in card.keys() and language != 'en' and language != 'ph':
        name_printed = card['printed_name']
        temp = language + '-' + name_printed + '.html'
        return temp.lower().replace('/', '-').replace(':', '').replace(' ', '-')

    return scryfall_uri.replace(
        'https://scryfall.com/card/' + set_code + '/' + collector_number + '/',
        '').replace('?utm_source=api', '').replace(
        '/', '-').replace(':', '').replace(' ', '-') + '.html'


def open_template(directory: str) -> str:
    '''
    Reads in the path of template.html and returns
    the file as a string
    '''
    template = open(directory, 'r')
    data = template.read()
    template.close()
    return data


def replace_data(data: str, card: dict) -> str:
    '''
    Replaces parts of the data string from template.html
    to create a unique string for a new webpage
    '''
    data = data.replace('Lightning Bolt', card['name'])
    data = data.replace('Magic 2010', card['set_name'].replace('’', "'"))

    if 'image_uris' in card.keys():
        data = data.replace(
            'https://c1.scryfall.com/file/scryfall-cards/large/front/4/3/435589bb-27c6-4a6d-9d63-394d5092b9d8.jpg?1561978182',
            card['image_uris']['large'])
    else:   # case for double-faced cards
        data = data.replace(
            'https://c1.scryfall.com/file/scryfall-cards/large/front/4/3/435589bb-27c6-4a6d-9d63-394d5092b9d8.jpg?1561978182',
            card['card_faces'][0]['image_uris']['large'])

    data = data.replace('output.data["M10"].cards[146-1].uuid', 'output.data["' + card['set'].upper() + '"].cards[' + card['collector_number'] + '-1].uuid')

    # generating a link for each alternate printing of a card
    if ENABLE_LINK_GENERATION:
        template = '<li class="list-group-item"><a href="../../2x2/361/lightning-bolt.html" class="link-primary">Double Masters 2022 #361</a></li>'                                
        replacement = ''

        other_printings = access_data(card['prints_search_uri'])

        for printing in other_printings['data']:    # ensures that a physical version of the card exists
            if 'tcgplayer_id' in printing.keys() and printing['digital'] == False:
                if card['set'] != printing['set'] or card['collector_number'] != printing['collector_number']:
                    href = '../../' + printing['set'] + '/' + printing['collector_number'] + '/' + create_file_name(printing)
                    temp = '<li class="list-group-item"><a href="../../2x2/361/lightning-bolt.html" class="link-primary">Double Masters 2022 #361</a></li>'
                    temp = temp.replace('../../2x2/361/lightning-bolt.html', href)
                    temp = temp.replace('Double Masters 2022 #361', printing['set_name'].replace('’', "'") + ' #' + printing['collector_number'])
                    
                    temp = temp.encode('ascii', 'ignore')   # ensures that there are no characters that html does not support
                    temp = temp.decode()
                    
                    replacement += temp

        if replacement != '': data = data.replace(template, replacement)
        else: data = data.replace(template, 'No alternate printings found')

    # generating purchase links for the card
    data = data.replace(
        'https://www.tcgplayer.com/product/32656',
        'https://www.tcgplayer.com/product/' + str(card['tcgplayer_id']))
    data = data.replace(
        'https://www.cardmarket.com/en/Magic/Products/Search?searchString=Lightning+Bolt',
        'https://www.cardmarket.com/en/Magic/Products/Search?searchString=' + card['name'].replace(' ', '+'))

    return data


def generate_webpage(directory: str, file_name: str, data: str) -> None:
    '''
    Reads in a file name and creates it
    at the specified directory using the
    data parameter
    '''
    try:
        set_path = pathlib.Path('/'.join(directory.split('/')[:-2]) + '/')
        if not set_path.exists(): set_path.mkdir()

        path = pathlib.Path(directory)
        if not path.exists(): path.mkdir()

        full_path = pathlib.Path(directory + file_name)
        if full_path.exists(): full_path.unlink()

        try:
            file = open(directory + file_name, 'w')
            file.write(data)
            file.close()
        except UnicodeEncodeError:  # if non ascii characters exist in the directory or file name
            pass
    except FileNotFoundError:   # if the set name is the name of reserved folders on Windows 10
        pass


if __name__ == '__main__':
    run()