import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fairview_org')



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess123=[]
    vurl = "https://fairview.org/coveo/rest/v2/"
    querystring = {"sitecoreItemUri":"sitecore://web/{6E683BED-A2BE-4806-B159-5E53407E019D}?lang=en&ver=1","siteName":"fairview","errorsAsSuccess":"1"}
    payload = "aq=((%40ftemplateid41631%3D%3D%22D52FB9B7-FD82-493F-9F2E-1B63EDD0E223%22%20OR%20%40ftemplateid41631%3D%3D%22E7333404-CEDD-4741-9142-BA4EEDDA7AEA%22%20OR%20%40ftemplateid41631%3D%3D%229CC6610A-5682-4CC7-A308-138C1A831E3D%22)%20AND%20%40fhidez32xfromz32xsearch41631%3D%220%22%20AND%20%40fhaslayout41631%3D%3D%221%22%20OR%20%40ftemplateid41631%3D%3D%2298BE4927-1BB3-443B-8834-03047126F32D%22)%20(%40flocationnetwork41631%3D%3DFairview)&cq=(%40fz95xlanguage41631%3D%3D%22en%22%20%40fz95xlatestversion41631%3D%3D%221%22)&language=en&firstResult=0&numberOfResults=204&excerptLength=200&enableDidYouMean=true&sortCriteria=%40flocationnetwork41631%20ascending%2C%20%40ftitle41631%20ascending&groupBy=%5B%7B%22field%22%3A%22%40flocationservicesandspecialties41631%22%2C%22sortCriteria%22%3A%22AlphaAscending%22%2C%22maximumNumberOfValues%22%3A100%2C%22queryOverride%22%3A%22((%40ftemplateid41631%3D%3D%5C%22D52FB9B7-FD82-493F-9F2E-1B63EDD0E223%5C%22%20OR%20%40ftemplateid41631%3D%3D%5C%22E7333404-CEDD-4741-9142-BA4EEDDA7AEA%5C%22%20OR%20%40ftemplateid41631%3D%3D%5C%229CC6610A-5682-4CC7-A308-138C1A831E3D%5C%22)%20AND%20%40fhidez32xfromz32xsearch41631%3D%5C%220%5C%22%20AND%20%40fhaslayout41631%3D%3D%5C%221%5C%22%20OR%20%40ftemplateid41631%3D%3D%5C%2298BE4927-1BB3-443B-8834-03047126F32D%5C%22)%20(%40flocationnetwork41631%3D%3DFairview)%22%2C%22constantQueryOverride%22%3A%22(%40fz95xlanguage41631%3D%3D%5C%22en%5C%22%20%40fz95xlatestversion41631%3D%3D%5C%221%5C%22)%22%7D%2C%7B%22field%22%3A%22%40fstandardlocationfeatures41631%22%2C%22sortCriteria%22%3A%22AlphaAscending%22%2C%22maximumNumberOfValues%22%3A100%2C%22queryOverride%22%3A%22((%40ftemplateid41631%3D%3D%5C%22D52FB9B7-FD82-493F-9F2E-1B63EDD0E223%5C%22%20OR%20%40ftemplateid41631%3D%3D%5C%22E7333404-CEDD-4741-9142-BA4EEDDA7AEA%5C%22%20OR%20%40ftemplateid41631%3D%3D%5C%229CC6610A-5682-4CC7-A308-138C1A831E3D%5C%22)%20AND%20%40fhidez32xfromz32xsearch41631%3D%5C%220%5C%22%20AND%20%40fhaslayout41631%3D%3D%5C%221%5C%22%20OR%20%40ftemplateid41631%3D%3D%5C%2298BE4927-1BB3-443B-8834-03047126F32D%5C%22)%20(%40flocationnetwork41631%3D%3DFairview)%22%2C%22constantQueryOverride%22%3A%22(%40fz95xlanguage41631%3D%3D%5C%22en%5C%22%20%40fz95xlatestversion41631%3D%3D%5C%221%5C%22)%22%7D%2C%7B%22field%22%3A%22%40flocationtypes41631%22%2C%22sortCriteria%22%3A%22AlphaAscending%22%2C%22maximumNumberOfValues%22%3A100%2C%22queryOverride%22%3A%22((%40ftemplateid41631%3D%3D%5C%22D52FB9B7-FD82-493F-9F2E-1B63EDD0E223%5C%22%20OR%20%40ftemplateid41631%3D%3D%5C%22E7333404-CEDD-4741-9142-BA4EEDDA7AEA%5C%22%20OR%20%40ftemplateid41631%3D%3D%5C%229CC6610A-5682-4CC7-A308-138C1A831E3D%5C%22)%20AND%20%40fhidez32xfromz32xsearch41631%3D%5C%220%5C%22%20AND%20%40fhaslayout41631%3D%3D%5C%221%5C%22%20OR%20%40ftemplateid41631%3D%3D%5C%2298BE4927-1BB3-443B-8834-03047126F32D%5C%22)%20(%40flocationnetwork41631%3D%3DFairview)%22%2C%22constantQueryOverride%22%3A%22(%40fz95xlanguage41631%3D%3D%5C%22en%5C%22%20%40fz95xlatestversion41631%3D%3D%5C%221%5C%22)%22%7D%2C%7B%22field%22%3A%22%40flocationnetwork41631%22%2C%22sortCriteria%22%3A%22AlphaAscending%22%2C%22maximumNumberOfValues%22%3A100%2C%22queryOverride%22%3A%22(%40ftemplateid41631%3D%3D%5C%22D52FB9B7-FD82-493F-9F2E-1B63EDD0E223%5C%22%20OR%20%40ftemplateid41631%3D%3D%5C%22E7333404-CEDD-4741-9142-BA4EEDDA7AEA%5C%22%20OR%20%40ftemplateid41631%3D%3D%5C%229CC6610A-5682-4CC7-A308-138C1A831E3D%5C%22)%20AND%20%40fhidez32xfromz32xsearch41631%3D%5C%220%5C%22%20AND%20%40fhaslayout41631%3D%3D%5C%221%5C%22%20OR%20%40ftemplateid41631%3D%3D%5C%2298BE4927-1BB3-443B-8834-03047126F32D%5C%22%22%2C%22constantQueryOverride%22%3A%22(%40fz95xlanguage41631%3D%3D%5C%22en%5C%22%20%40fz95xlatestversion41631%3D%3D%5C%221%5C%22)%22%7D%5D&retrieveFirstSentences=true&timezone=America%2FLos_Angeles&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false"
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        }

    response = session.post( vurl, data=payload, headers=headers, params=querystring)
    locator_domain ='https://fairview.org'
    for value in json.loads(response.text)['results']:

        page_url = value['ClickUri']
        # logger.info(page_url)
        hours1='<MISSING>'
        jdata= json.loads(value['raw']['flocationdisplaycontent41631'])
        if jdata==None:
            continue
        try:
            location_name = jdata['Title']
        except:
            location_name = "<MISSING>"
        # logger.info(location_name)
        # exit()
        response = session.post(page_url)
        soup = BeautifulSoup(response.text,'lxml')
        # logger.info(soup.find("div",{"class":"hours-contact rte"}).find("h2").text)
        # logger.info(page_url)
        hours = soup.find(lambda tag: (tag.name == "h4") and "Hours" == tag.text.strip())
        if hours != None:
            hours1=' '.join(list(hours.parent.stripped_strings))
        else: 
            hours1 = "<MISSING>"
        if hours1=="Hours":
            hours1 = "<MISSING>"
        
        street_address =jdata['Address']['StreetAddress1']
        city = jdata['Address']['City']
        state = jdata['Address']['State']
        zipp = jdata['Address']['Zip']
        latitude = jdata['Address']['Latitude']
        longitude = jdata['Address']['Longitude']
        # logger.info(jdata['LocationPhones'])
        if "DisplayNumber" in  jdata['LocationPhones'][0]:
            phone = jdata['LocationPhones'][0]['DisplayNumber']
        if phone == "":
            phone = jdata['LocationPhones'][1]['DisplayNumber']
        if "FAIRVIEW" in phone:
            phone=phone.replace("-FAIRVIEW",'').replace("FAIRVIEW",'')
        phone = phone.split(";")[0].strip()
        # logger.info(phone)
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        street_address = street_address.split('Suite')[0].split('Floor')[0].replace(",",'')
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone.replace('612-336-2670 or 1-844-858-2670','612-336-2670'), location_type, latitude, longitude, hours1.replace('Hours','').strip(), page_url]
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        
        if store[1]+store[2]  in addressess123:
            continue
        addressess123.append(store[1]+store[2])
        # logger.info(store)
        yield store


          
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
