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
    p = 0
    all = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.bobaguys.com/'
    r = session.get(url, headers=headers, verify=False)
   
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup.find('li', {'class': 'folder'}))
    urls = soup.find('li', {'class': 'folder'}).find_all('a')
    del urls[0]

    for url in urls:
        url = "https://www.bobaguys.com"+url['href']
        res = session.get(url)

        soup = BeautifulSoup(res.text, 'html.parser')
        divs = soup.find_all('div', {'class': 'col sqs-col-4 span-4'})
        if len(divs)==0:
            divs = soup.find_all('div', {'class': 'col sqs-col-6 span-6'})
        #print(url)
        for div in divs:

            ps=div.find('div',{'class':'sqs-block html-block sqs-block-html'}).find_all('p')
            
            #print(len(ps))
            #print(ps[0])
            if len(ps)==2:
                #print(ps[1])
                try:
                    loc,street,city,state,zip=re.findall(r'<strong>(.*)</strong><br/>(.*)<br/>(.*), ([A-Z]{2}) ([\d]{5})</p>',str(ps[0]))[0]
                except:
                    try:
                        loc, street, city, state, zip = re.findall(r'<strong>(.*)</strong><br/>(.*)<br/>(.*) ([A-Z]{2}) ([\d]{5})</p>', str(ps[0]))[0]
                    except:
                        #print('no')
                        content = re.sub(cleanr,'\n',str(ps[0]))
                        content = re.sub(pattern,'\n',content.lstrip()).lstrip().splitlines()
                        
                        #print(content)
                        #loc, street, city, zip=re.findall(r'<strong>(.*)</strong><br/>(.*)<br/>(.*) ([\d]{5})</p>', str(ps[0]))
                        loc = content[0]
                        street = content[1]                       
                        zip = content[2].split(' ')[-1]
                        city = content[2].replace(zip,'').lstrip()
                        try:
                            city,state = city.split(', ')
                        except:
                            state="<MISSING>"
                if "Temporarily Closed" in str(ps[1]):
                    tim="<MISSING>"
                    type = "Temporarily Closed"
                else:
                    tim=ps[1].text.replace('mS','m S').replace('dS','d S')
                    type = "Open"
            else:
                try:
                    loc, street, city, state, zip =re.findall(r'<strong>(.*)</strong><br/>(.*)<br/>(.*), ([A-Z]{2}) ([\d]{5}).*<strong>', str(ps[0]))[0]
                except:
                    loc, street, city, state, zip =re.findall(r'<strong>(.*)<br/></strong>(.*)<br/>(.*), ([A-Z]{2}) ([\d]{5}).*<strong>', str(ps[0]))[0]
                if "Temporarily Closed" in str(ps[0]):
                    tim="<MISSING>"
                    type = "Temporarily Closed"
                else:
                    type="Open"
                    tim=ps[0].find_all('strong')[1].text
                    if tim.strip()=="":
                        tim="".join(re.findall(r'.*<strong>(.*)</strong>(.*)</p>',str(ps[0]))[0])
            all.append([
                "https://www.bobaguys.com",
                url,
                loc,
                street,
                city,
                state,
                zip,
                "US",
                "<MISSING>",  # store #
                "<MISSING>",  # phone
                "<MISSING>",  # type
                "<MISSING>",  # lat
                "<MISSING>",  # long
                tim  # timing
                ])
            #print(p,all[p])
            p += 1

   
    return all


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
