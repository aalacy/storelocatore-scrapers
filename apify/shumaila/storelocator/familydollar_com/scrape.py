#
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('familydollar_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    # Your scraper here
    states = ["AL", "AK", "AZ", "AR", "CA", "CO",
    "CT","DC","DE", "FL", "GA","HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO",
    "MT","NE","NV", "NH", "NJ", "NM", "NY",
    "NC", "ND", "OH", "OK", "OR", "PA",
    "RI", "SC","SD", "TN", "TX", "UT",
    "VT", "VA", "WA", "WV", "WI", "WY"] 
    data = []

    pattern = re.compile(r'\s\s+')

    p = 0
    for i in range(0,len(states)):
        logger.info(states[i])          
        url = 'https://locations.familydollar.com/ajax?&xml_request=%3Crequest%3E%20%3Cappkey%3ED2F68B64-7E11-11E7-B734-190193322438%3C/appkey%3E%20%3Cgeoip%3E1%3C/geoip%3E%20%3Cformdata%20id=%22getlist%22%3E%20%3Cobjectname%3ELocator::Store%3C/objectname%3E%20%3Cwhere%3E%20%3Ccity%3E%3Ceq%3E%3C/eq%3E%3C/city%3E%20%3Cstate%3E%3Ceq%3E'+states[i]+'%3C/eq%3E%3C/state%3E%20%3C/where%3E%20%3C/formdata%3E%20%3C/request'
      
        page = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(page.text,"html.parser")
        #logger.info(soup)
        
        repo_list = soup.findAll('poi')
        logger.info(len(repo_list))
      
        for repo in repo_list:

            title = repo.find('name').text
            street = repo.find('address1').text
            city = repo.find('city').text
            lat = repo.find('latitude').text
            longt =  repo.find('longitude').text
            phone=  repo.find('phone').text
            store = repo.find('store').text
            state = repo.find('state').text
            pcode = repo.find('postalcode').text
            hours = ''
            try :
                
                hours = hours + "Monday : "+repo.find('monopen').text +' - '+ repo.find('monclose').text +', '
            except:
                pass
            try :
                hours = hours + "Tuesday : "+repo.find('tueopen').text +' - '+ repo.find('tueclose').text +', '
            except:
                pass
            try :
                hours = hours + "Wednesday : "+repo.find('wedopen').text +' - '+ repo.find('wedclose').text +', '
            except:
                pass
            try :
                hours = hours + "Thursday : "+repo.find('thuopen').text +' - '+ repo.find('thuclose').text +', '
            except:
                pass
            try :
                hours = hours + "Friday : "+repo.find('friopen').text +' - '+ repo.find('friclose').text +', '
            except:
                pass
            try :
                hours = hours + "Saturday : "+repo.find('satopen').text +' - '+ repo.find('satclose').text +', '
            except:
                pass
            try :
                hours = hours + "Sunday : "+repo.find('sunopen').text +' - '+ repo.find('sunclose').text +', '
            except:
                pass
           
            street = street.replace('Distribution Center','')
            street = street.replace('-','')
            street = street.lstrip()
            start = hours.find(':')+1
            end = hours.find('-',start)
            temp = hours[start:end]
            if len(temp) < 3:
                hours = "<MISSING>"
            else:
                hours = hours.rstrip()
                hours = hours[0:len(hours)-1]
            
            if len(phone) < 3:
                phone = "<MISSING>"
            if len(street) < 3:
                street = "<MISSING>"
            if len(city) < 3:
                city = "<MISSING>"
            if len(state) < 2:
                state = "<MISSING>"
            if len(pcode) < 3:
                pcode = "<MISSING>"
            if len(store) < 1:
                store = "<MISSING>"
            if len(lat) < 3:
                lat = "<MISSING>"
            if len(longt) < 3:
                longt = "<MISSING>"

            
            data.append(['https://www.familydollar.com/',"<MISSING>",title,street,city,state,pcode,'US',store,phone,"<MISSING>",lat,longt,hours])
            #logger.info(p,data[p])           
            p += 1
            
            
    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

