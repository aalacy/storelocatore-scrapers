import csv
import urllib2
import requests

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'cookie': 'visid_incap_1768624=aOghFF8eT8qdKtwbh+jbCLQfUl0AAAAAQUIPAAAAAACy9dA4eFVhiXJCnPz1pM/e; incap_ses_117_1768624=0DnZRQ/uogs4voaAvqufAbQfUl0AAAAAwU+q6oaQIUwuPsk2wp4Dpw==; _ga=GA1.2.1290702306.1565663159; _gid=GA1.2.1716743534.1565663159; incap_ses_115_1768624=cOD0Us1U5SnWFuQ9s5CYATLHUl0AAAAAwcMPKUOzqGp8ap+xZGLlOg=='
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    r = session.get('https://www.etgrill.com', headers=headers)
    url = 'https://www.etgrill.com/menu_location-sitemap.xml'
    r = session.get(url, headers=headers)
    locs = []
    for line in r.iter_lines():
        if '<loc>' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            locs.append(lurl.replace('menu-location','contact'))
    for loc in locs:
        loc_text = session.get(loc, headers=headers)
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        hours = ''
        name = ''
        for line2 in loc_text.iter_lines():
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' - ')[0]
            if 'Address &amp; Phone</h3><p style="text-align: center;">' in line2:
                fulladd = line2.split('Address &amp; Phone</h3><p style="text-align: center;">')[1].split('</p>')[0]
                phone = line2.split('Address &amp; Phone</h3><p style="text-align: center;">')[1].split('<p style="text-align: center;">')[1].split('<')[0]
                add = fulladd.split('<')[0]
                city = fulladd.split('>')[1].split(',')[0].strip()
                state = fulladd.split('>')[1].split(',')[1].strip().split(' ')[0]
                zc = fulladd.rsplit(' ',1)[1]
            if 'HOURS</h3><p style="text-align: center;">' in line2:
                hours = line2.split('HOURS</h3><p style="text-align: center;">')[1].split('</div>')[0]
                hours = hours.replace('&#8211;','-').replace('<br/>',';').replace('</p>','')
        yield ["etgrill.com", name, add, city, state, zc, "US", "<MISSING>", phone, "Restaurant", "<MISSING>", "<MISSING>", hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
