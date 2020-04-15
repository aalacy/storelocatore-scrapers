import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',    
    }

    base_url = "https://www.metrohealth.org/"   
    data = "aq=(%40distance%20%3C160934000)%20(%40fz95xpath64997%3D%3D1ebfab597c544c279a47c940ffdb8757)%20(%40falltemplates64997%3D%3Dda75008d42a14084b9e3db3d27907e37)%20(%24qf(function%3A'dist(%40flatitude64997%2C%40flongitude64997%2C41.46098%2C-81.6988)'%2C%20fieldName%3A%20'distance'))%20(%40syssource%3D%3D%22Coveo_web_index%20-%20mhs-production-farm%22)&cq=(%40fz95xlanguage64997%3D%3Den)%20(%40fz95xlatestversion64997%3D%3D1)&searchHub=locations&language=en&firstResult=0&numberOfResults=1000&excerptLength=200&enableDidYouMean=false&sortCriteria=fieldascending&sortField=%40distance&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%7B%22field%22%3A%22%40frelatedspecialtynames64997%22%2C%22maximumNumberOfValues%22%3A999%2C%22sortCriteria%22%3A%22alphaascending%22%2C%22injectionDepth%22%3A1000%7D%5D&retrieveFirstSentences=true&timezone=Asia%2FCalcutta&enableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false"  

    r = session.post("https://www.metrohealth.org/coveo/rest/v2/?sitecoreItemUri=sitecore%3A%2F%2Fweb%2F%7B035E8482-333E-4D02-AF8A-EBC88B3AD984%7D%3Flang%3Den%26amp%3Bver%3D2&siteName=mhs", headers=headers, data=data).json()['results']

    for data in r:
        location_name = data['raw']['systitle']
        street_address = data['raw']['faddressz32xlinez32x164997']
        city = data['raw']['fcity64997']
        state = data['raw']['fstate64997']
        zipp = data['raw']['fz122xipcode64997']
        latitude = data['raw']['flatitude64997']
        longitude = data['raw']['flongitude64997']
        try:
            phone = data['raw']['fprimaryz32xphone64997']
        except:
            phone = "<MISSING>"
        page_url = data['clickUri']
        # print(page_url)
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        try:
            hours = " ".join(list(soup1.find("div",{"class":"col-md-3 col-6 loc-hours"}).find("span").stripped_strings)).replace("Level I Trauma Center and Comprehensive Stroke Center","")
        except:
            hours = "<MISSING>"
        store = []  
        
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp if zipp else "<MISSING>")   
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("MetroHealth")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        # print("data==="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

        yield store
        

        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
