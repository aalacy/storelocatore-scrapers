import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import time
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = "https://www.sanfordhealth.org/coveo/rest/v2/"

    querystring = {"sitecoreItemUri":"sitecore://web/{AA2CFD83-3371-4D1E-913E-A23FF93C9E56}?lang=en&ver=1","siteName":"ORG"}

    payload = "aq=%40syssource%3D%3D(%22ORG_coveo_web_index%20-%20sanford-coveo-prod%22)%20((%40fz95xpath46747%3D%3D%22AA2CFD8333714D1E913EA23FF93C9E56%22)%20(%40fhaslayout46747%3D%3D%221%22)%20(%40fz95xtemplate46747%3D%3D%22F8CF55EA84BB4E58B7B08A39596DCCD6%22))%20NOT%20%40ftemplateid46747%3D%3D(%22adb6ca4f-03ef-4f47-b9ac-9ce2ba53ff97%22%2C%22fe5dd826-48c6-436d-b87a-7c4210c7413b%22)&cq=(%40fz95xlanguage46747%3D%3D%22en%22%20%40fz95xlatestversion46747%3D%3D%221%22)&searchHub=ORG%20locations&language=en&pipeline=ORG&firstResult=0&numberOfResults=514&excerptLength=200&enableDidYouMean=true&sortCriteria=relevancy&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%7B%22field%22%3A%22%40ffacilitytype46747%22%2C%22maximumNumberOfValues%22%3A101%2C%22sortCriteria%22%3A%22alphaascending%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%7D%2C%7B%22field%22%3A%22%40flocationservice46747%22%2C%22maximumNumberOfValues%22%3A301%2C%22sortCriteria%22%3A%22alphaascending%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%7D%2C%7B%22field%22%3A%22%40flocationstate46747%22%2C%22maximumNumberOfValues%22%3A101%2C%22sortCriteria%22%3A%22alphaascending%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%7D%2C%7B%22field%22%3A%22%40fcity46747%22%2C%22maximumNumberOfValues%22%3A201%2C%22sortCriteria%22%3A%22alphaascending%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%7D%5D&retrieveFirstSentences=true&timezone=America%2FLos_Angeles&disableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false&context=%7B%7D"
    headers = {
        'accept': "*/*",
        'content-type': "application/x-www-form-urlencoded",
        'sec-fetch-dest': "empty",
        'sec-fetch-mode': "cors",
        'sec-fetch-site': "same-origin",
        }

    response = session.post(url, data=payload, headers=headers, params=querystring)
    jason_data=(json.loads(response.text))
    addressesess=[]
    for anchor in jason_data['results']:

        if "Title" in anchor:
            location_name = anchor['Title']
        else:
            location_name = "<MISSING>"

        street_address = anchor['raw']['faddress46747']
        if "clickUri" in anchor:
            page_url = anchor['clickUri']
        else:
            page_url = "<MISSING>"
        city = anchor['raw']['fcity46747'][0]
        if "flocationstate46747" in anchor['raw']:
            state = anchor['raw']['flocationstate46747']
        else:
            state = "<MISSING>"
        if state == "Greater Accra" or state == "Central":
            continue
        if "fpostalcode46747" in anchor['raw']:
            zipp = anchor['raw']['fpostalcode46747']
        else:
            zipp = "<MISSING>"

        if "fphone46747" in anchor['raw']:
            phone = anchor['raw']['fphone46747']
        else:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        if "flatitude46747" in anchor['raw']:
            latitude = anchor['raw']['flatitude46747']
            longitude = anchor['raw']['flongitude46747']
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"


        if "fprimaryhours46747" in anchor['raw']:
            hours =anchor['raw']['fprimaryhours46747']
        
        hours_of_operation = hours

        # flabhours46747
        # foperatinghours46747

        store = []
        store.append("https://www.sanfordhealth.org/")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation.strip().replace("\n"," ") if hours_of_operation else "<MISSING>")
        store.append(page_url)
        # store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store
        
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

