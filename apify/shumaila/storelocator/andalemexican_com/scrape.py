from bs4 import BeautifulSoup
import csv, re
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain",'page_url', "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    cleanr = re.compile(r'<[^>]+>')
    pattern = re.compile(r'\s\s+') 
    data = []
    p = 0
    url = 'https://www.andalemexican.com/locations'
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    repo_list = soup.findAll('div', {'class': 'summary-content sqs-gallery-meta-container'})
    print(len(repo_list))
    
    for repo in repo_list:
        title = repo.find('a',{'class':'summary-title-link'})
        link = 'https://www.andalemexican.com' +title['href']
        title= title.text
        content = repo.find('div',{'class':'summary-excerpt'}).findAll('p')
        for ct in content:
            if ct.text.find("Fax") > -1:
                address = ct
            elif ct.text.find("Hours") > -1:
                hours = ct.text
        #address = content[3]
        address= re.sub(cleanr,'\n',str(address))
        address= re.sub(pattern,'\n',address.lstrip()).split('\n')
        #print(address)
        #hours = content[4].text
        street = address[0]      
        city,state = address[1].split(', ',1)
        try:
            state,pcode = state.lstrip().split(' ',1)
        except:
            pcode = '<MISSING>'
        phone = address[2]
       
        data.append([
            'https://www.andalemexican.com/locations',
            link,
            title,
            street,
            city,
            state,
            pcode,
            'US',
            "<MISSING>",
            phone,
            "<MISSING>",
            "<MISSING>",
            "<MISSING>",
            hours.replace('Hours:','')
        ])

        #print(p,data[p])
        p += 1
        
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
