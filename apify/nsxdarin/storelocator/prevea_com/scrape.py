import csv
import urllib2
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'cookie': 'ARRAffinity=2d91f0baa57ab6b4e5517a3c943caf4da46f1db9f9b3053309006dfe168b2f80; CMSPreferredCulture=en-US; CMSCsrfCookie=YhpxbZcD6zSCJZUvFAPl04+EbMgafM1p4VW8scLQ; ASP.NET_SessionId=olxbc342wckhhqhggwtbp4sy; CurrentContact=47bce9ed-997d-415f-afe1-5d85dc6b1f5e; CMSLandingPageLoaded=true; btpdb.dcKDAzq.dGZjLjc0MDY1NjQ=U0VTU0lPTg; nmstat=1588195767765; _gcl_au=1.1.1604847786.1588195674; prism_799401111=781c612f-487d-444e-9169-8afd25f800a7; _ga=GA1.2.625879050.1588195674; _gid=GA1.2.1401364951.1588195674; _fbp=fb.1.1588195674724.895817265; btpdb.dcKDAzq.dGZjLjcwNDQxNTM=U0VTU0lPTg; _gat_UA-901569-1=1; VisitorStatus=11062063222; CMSUserPage={"TimeStamp":"2020-04-29T21:42:03.2627914+00:00","LastPageDocumentID":95,"LastPageNodeID":97,"Identifier":"6ef6f6e7-5395-41eb-971e-7256cf2dcc95"}'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.prevea.com/providers?loadmap=1'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<strong><a href=\\"/locations' in line:
            locs.append('https://www.prevea.com/locations' + line.split('<strong><a href=\\"/locations')[1].split('\\')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'prevea.com'
        typ = ''
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = '<MISSING>'
        phone = ''
        lat = ''
        lng = ''
        Found = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '"@context": "' in line2:
                Found = True
            if Found and ',"isAcceptingNewPatients":' in line2:
                Found = False
            if Found and '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if Found and '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0]
            if Found and '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if Found and '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if Found and '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if Found and '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if Found and '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if Found and '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '<h4><em><strong>' in line2:
                tname = line2.split('<h4><em><strong>')[1].split('<')[0]
                if typ == '':
                    typ = tname
                else:
                    typ = typ + ', ' + tname
        if hours == '':
            hours = '<MISSING>'
        if typ == '':
            typ = '<MISSING>'
        if ', Suite' in add:
            add = add.split(', Suite')[0]
        if ', Inside' in add:
            add = add.split(', Inside')[0]
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
