from bs4 import BeautifulSoup
import csv
import string
import re, time, json

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
    titlelist = []
    state_list = []
    pattern = re.compile(r'\s\s+')
    url = 'https://www.extraspace.com/help/accessibility-commitment/'
    try:
        r = session.get(url)

    except:
        pass
    
    
    soup =BeautifulSoup(r.text, "html.parser")   
    maindiv = soup.findAll('a')
    for lt in maindiv:
        try:
            if lt['href'].find('SiteMap-') > -1:
                state_list.append("https://www.extraspace.com" + lt['href'])
        except:
            pass
        
   
    p = 0
    for alink in state_list:       
        statelink = alink #"https://www.extraspace.com" + alink['href']
        #print(statelink)
        try:
            r1 = session.get(statelink, headers=headers, verify=False)#requests.get(statelink,timeout = 30)
        except:
            pass
  
        soup1 =BeautifulSoup(r1.text, "html.parser")
        maindiv1 = soup1.find('div',{'id':'acc-main'})
        #print(maindiv1)
        link_list = maindiv1.findAll('a')
        #print("NEXT PAGE",len(link_list))
        for alink in link_list:
            if alink.text.find('Extra Space Storage #') > -1:
                link = "https://www.extraspace.com" + alink['href']
                #print(link)
                #input()
                
                r2 = session.get(link, headers=headers, verify=False)
                
  
                content = r2.text.split(' "@type": "SelfStorage",',1)[1].split('</script>')[0]
                content = '{'+content
                content = json.loads(content)
                city = content['address']["addressLocality"]
                state = content['address']["addressRegion"]
                pcode = content['address']["postalCode"]
                street = content['address']["streetAddress"]
                title = content['name']
                phone = content['telephone'].replace('+1-','')
                lat = content['geo']['latitude']
                longt = content['geo']['longitude']
                hourslist = BeautifulSoup(r2.text,'html.parser').text.split('Storage Office Hours',1)[1].splitlines()[0:10]
                hours = ''
                for hr in hourslist:
                    if ('am' in hr and 'pm' in hr) or 'closed' in hr:
                        hours = hours + hr + ' '
                    elif hr == ' ':
                        break
               
                
                hours = hours.replace('am', ' am ').replace('pm',' pm ').replace('-',' - ')
                try:
                    hours = hours.split('CUT THE LIN',1)[0].strip()
                except:
                    pass
                try:
                    hours = hours.split('closed',1)[0]
                    hours = hours + 'closed'
                except:
                    pass
                
                store = link.split('/')[-2]

                if street in titlelist:
                    continue
                titlelist.append(street)
                data.append([
                        'https://www.extraspace.com',
                        link,
                        title,
                        street.replace('<br />',' '),
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        phone,
                        "<MISSING>",
                        lat,
                        longt,
                        hours
                    ])
                #print(p,data[p])
                p += 1
                    
            
      
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

