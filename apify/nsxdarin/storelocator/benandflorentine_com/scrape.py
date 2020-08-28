import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://benetflorentine.com/en/restaurants/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '"locations":[' in line:
            line = line.replace(',"categories":[{"title":"','').replace(':null},{"title":"','')
            items = line.split('{"title":"')
            for item in items:
                if '"cssClass":"' in item:
                    website = 'benandflorentine.com'
                    country = 'CA'
                    purl = '<MISSING>'
                    name = item.split('"')[0].replace('\\u00e9','e')
                    addinfo = item.split('"description":"<p>')[1].split('<\\/p>')[0].replace(', QC',', QC,').replace(', MB',', MB,').replace(', ON',', ON,').replace(',,',',')
                    add = addinfo.split('<')[0]
                    if '2817 avenue des' in add:
                        zc = 'H7E 0H3'
                        state = 'QC'
                        city = 'Laval'
                    elif '1340 Casa' in add:
                        zc = 'J2S 0G2'
                        state = 'QC'
                        city = 'Saint-Hyacinthe'
                        add = '1340 Casavant E. Blvd.'
                    elif '174 St L' in add:
                        zc = 'J2W 0J2'
                        state = 'QC'
                        city = 'Saint-Jean-sur-Richelieu'
                        add = '174 St Luc Blvd.'
                    if '2817 avenue des' in add:
                        zc = 'H7E 0H3'
                        state = 'QC'
                        city = 'Laval'
                    elif '1340 Casa' in add:
                        zc = 'J2S 0G2'
                        state = 'QC'
                        city = 'Saint-Hyacinthe'
                        add = '1340 Casavant E. Blvd.'
                    elif '174 St L' in add:
                        zc = 'J2W 0J2'
                        state = 'QC'
                        city = 'Saint-Jean-sur-Richelieu'
                        add = '174 St Luc Blvd.'
                    elif '203 Cur' in add:
                        add = '203 Cure-Labelle Blvd.'
                        city = 'Saint-Therese'
                        state = 'QC'
                        zc = 'J7E 2X6'
                    elif '250 Fiset' in add:
                        add = '250 Fiset Blvd.'
                        city = 'Sorel-Tracy'
                        state = 'QC'
                        zc = 'J3P 3P7'
                    elif '970 des' in add:
                        add = '970 des Ibis Street'
                        city = 'Val-Belair'
                        state = 'QC'
                        zc = 'G3K 0S4'
                    elif '48 de la' in add:
                        add = '48 de la Cite des Jeunes Blvd.'
                        city = 'Vaudreuil-Dorion'
                        state = 'QC'
                        zc = 'J7V 9L5'
                    else:
                        city = addinfo.split('<br \\/>\\n')[1].split(',')[0].strip()
                        state = addinfo.split('\\n')[1].split(',')[1].strip()
                        zc = addinfo.split('\\n')[1].split(',')[2].strip()
                    try:
                        lat = item.split('\\/@')[1].split(',')[0]
                        lng = item.split('\\/@')[1].split(',')[1]
                    except:
                        lat = '<MISSING>'
                        lng = '<MISSING>'
                    store = '<MISSING>'
                    typ = '<MISSING>'
                    if zc == '':
                        zc = '<MISSING>'
                    desc = item.split('"simpledescription":"')[1].split('\\n<p><a href=')[0]
                    hours = desc.split('<\\/p>\\n<p>')[1].replace('<br \\/>\\n','; ')
                    if '<\\/p>' in hours:
                        hours = hours.split('<')[0]
                        phone = hours.split('; ')[1]
                    else:
                        phone = desc.split('<\\/p>\\n<p>')[2].split('<')[0]
                    yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
