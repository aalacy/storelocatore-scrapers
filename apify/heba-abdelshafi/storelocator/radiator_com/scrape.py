from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.radiator.com/SiteMap'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")
    titlelist = []
    divlist = soup.select("a[href*=locations]")
    states = {
    'alabama': 'AL','alaska': 'AK','arizona': 'AZ','arkansas': 'AR','california': 'CA',
    'colorado': 'CO','connecticut': 'CT','delaware': 'DE',
    'district of columbia': 'DC','florida': 'FL','georgia': 'GA','hawaii': 'HI',
    'idaho': 'ID','illinois': 'IL','indiana': 'IN','iowa': 'IA','kansas': 'KS',
    'kentucky': 'KY','louisiana': 'LA','maine': 'ME','maryland': 'MD','massachusetts': 'MA',
    'michigan': 'MI','minnesota': 'MN','mississippi': 'MS',
    'missouri': 'MO',
    'montana': 'MT',
    'nebraska': 'NE',
    'nevada': 'NV',
    'new hampshire': 'NH',
    'new jersey': 'NJ',
    'new mexico': 'NM',
    'new york': 'NY',
    'north carolina': 'NC',
    'north Dakota': 'ND',
    'northern Mariana Islands':'MP',
    'ohio': 'OH',
    'oklahoma': 'OK',
    'oregon': 'OR',
    'pennsylvania': 'PA',
    'puerto rico': 'PR',
    'rhode island': 'RI',
    'south carolina': 'SC',
    'south dakota': 'SD',
    'tennessee': 'TN',
    'texas': 'TX',
    'utah': 'UT',
    'vermont': 'VT',
    'virgin islands': 'VI',
    'virginia': 'VA',
    'washington': 'WA',
    'west virginia': 'WV',
    'wisconsin': 'WI',
    'wyoming': 'WY'
}

   # print("states = ",len(state_list))
    p = 0
    for div in divlist:
        #print(div['href'])
        if div['href'].find('locations/') == -1:
            continue
        
        link = div['href']
        r = session.get(link, headers=headers, verify=False)  
        soup = BeautifulSoup(r.text,'html.parser')
        title = soup.find('div',{'class':'locationContent'}).text.lstrip().split('\n',1)[0]
        
        content = soup.find('div',{'class':'locationContent'})
        street = content.find('span',{'class':'address-address'}).text
        city = content.find('span',{'class':'address-city'}).text
        state =content.find('span',{'class':'address-state'}).text
        ccode = content.find('span',{'class':'address-country'}).text
        pcode = content.find('span',{'class':'address-zip'}).text
        try:
            phone = content.select_one('span:contains("Phone")').text.split(': ')[1]
        except:
            phone = '<MISSING>'
        lat = content.find('input',{'class':"address-latitude"})['value']
        longt = content.find('input',{'class':"address-longitude"})['value']
        
        if ccode == 'US':
            if state == 'OAKLAHOMA':
                state = 'OKLAHOMA'
            if state.find(' OR') > -1:
                state = 'OREGON'
            state=states[state.lower()]

        if street in titlelist:
            continue
        if state == 'TORONTO':
            state = 'ON'
        titlelist.append(street)
        data.append([
            'https://www.radiator.com/',
            link,                   
            title,
            street,
            city,
            state,
            pcode,
            ccode,
            '<MISSING>',
            phone,
            '<MISSING>',
            lat,
            longt,
            '<MISSING>'
        ])
        #print(p,data[p])
        p += 1

        
    return data


def scrape():
   
    data = fetch_data()
    write_output(data)
   

scrape()
