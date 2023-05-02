# divides MTGJSON's AllPrices.json file into an individual
# json file for each card that exists with the file name
# being the card's MTGJSON UUID
#
# https://mtgjson.com/

import pathlib
import json

path = 'webpage/AllPrices.json'
location = 'webpage/AllPrices'

location_path = pathlib.Path(location)
if not location_path.exists(): location_path.mkdir()

file = open(path,'r',encoding='utf-8')
data = json.load(file)

for key, object in data['data'].items():
    print(key)

    file_name = key + '.json'

    new_file = open(location + '/' + file_name, 'w')
    json.dump(object, new_file, indent=4)

print()
print('Splitting complete!')
print()