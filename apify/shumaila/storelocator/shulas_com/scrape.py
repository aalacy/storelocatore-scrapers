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
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://shulassteakhouse.com/#locations'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.findAll('div', {'class': "shula-menu__location"})
   # print("states = ",len(state_list))
    p = 0
    flag = 0
    for div in divlist:
        if True:
            link =  div.find('a')['href']
            #link = 'https://shulasbarandgrill.com/'
            #print(link)
            
            r = session.get(link, headers=headers, verify=False)
            if link == 'https://shulasbarandgrill.com/' and flag == 0:
                flag = 1
                soup = BeautifulSoup(r.text,'html.parser')
                titlelist= soup.findAll('div',{'class':'location'})
                addresslist = soup.findAll('div',{'class':'location-info'})
                for i in range(0,len(titlelist)):
                    title = titlelist[i].text
                    address = addresslist[i].text.splitlines()
                    #print(address)
                    city,state = address[-1].split(', ')
                    state,pcode = state.lstrip().split(' ',1)
                    street = ' '.join(address[0:len(address)-1])
                    #print(street)
                    data.append([
                        'https://shulas.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>'
                    ])
                    #print(p,data[p])
                    p += 1
                
                continue
            try:
                title = div.find('a').text
                jslink ='https://knowledgetags.yextpages.net'+ r.text.split('https://knowledgetags.yextpages.net',1)[1].split('"',1)[0]
                print(jslink)
                r = session.get(jslink, headers=headers, verify=False)
                address = r.text.split('"address":{',1)[1].split('}',1)[0]
                address = '{' +address + '}'
                address = json.loads(address)
                street = address['streetAddress']
                city = address['addressLocality']
                state = address['addressRegion']
                pcode = address['postalCode']
                try:
                    phone = r.text.split('"telephone":"',1)[1].split('"')[0].replace('+1','')
                except:
                    phone = '<MISSING>'
            
                hourlist = r.text.split('"openingHoursSpecification":[',1)[1].split('],',1)[0]
                hourlist = '['+hourlist+']'
                hourlist = json.loads(hourlist)
                hours = ''
                try:
                    for hour in hourlist:
                        starttime = hour['opens']
                        start = (int)(starttime.split(':')[0])
                        if start > 12:
                            start = start -12
                        endtime = hour['closes']
                        end = (int)(endtime.split(':')[0])
                        if end > 12:
                            end = end -12
                            
                            
                        hours = hours + hour['dayOfWeek']+' '+str(start) +':'+starttime.split(':')[1] + ' AM - ' +str(end) +':'+endtime.split(':')[1] + ' PM  '
                except:
                    hours = '<MISSING>'
                    
                
                try:
                    lat = r.text.split('"latitude":',1)[1].split(',')[0]
                except:                    
                    lat = '<MISSING>'
                try:
                    longt = r.text.split('"longitude":',1)[1].split('}')[0]
                except:                    
                    longt = '<MISSING>'
                
                data.append([
                        'https://shulas.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        hours
                    ])
                #print(p,data[p])
                p += 1
                
                    
            
            except Exception as e:
                #print(e)
                pass
        
           
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
