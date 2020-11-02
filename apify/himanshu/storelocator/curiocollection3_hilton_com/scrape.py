import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('curiocollection3_hilton_com')


def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
session = SgRequests()
def fetch_data():
    address = []
    headers = {
        'Content-Type':'application/json',
        'cache-control': "no-cache",
    }
    url = "https://www.hilton.com/graphql/customer?appName=dx-shop-dream-ui&operationName=hotelMapZones"
    payload = "{\"operationName\":\"hotelMapZones\",\"variables\":{\"brandCode\":\"\"},\"query\":\"query hotelMapZones($brandCode: String) {\\n  hotelMapZones(brandCode: $brandCode) {\\n    id {\\n      x\\n      y\\n      __typename\\n    }\\n    bounds {\\n      southwest {\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      northeast {\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      __typename\\n    }\\n    countries {\\n      countryCode\\n      stateCodes\\n      __typename\\n    }\\n    brandCodes\\n    __typename\\n  }\\n}\\n\"}"
    data = session.post(url,data=payload,headers=headers).json()
    # logger.info(data)
    for zone in data['data']['hotelMapZones']:
        url = "https://www.hilton.com/graphql/customer"
        querystring = {"appName":"dx-shop-dream-ui","operationName":"hotelSummaryOptions","queryType":"zone"}
        payload = "{\"operationName\":\"hotelSummaryOptions\",\"variables\":{\"brandCodes\":[],\"currencyCode\":\"usd\",\"language\":\"en\",\"zone\":{\"x\":"+str(zone['id']['x'])+",\"y\":"+str(zone['id']['y'])+"}},\"query\":\"query hotelSummaryOptions($brandCodes: [String!]!, $currencyCode: String!, $language: String!, $zone: HotelZoneInput) {\\n  hotelSummaryOptions(brandCodes: $brandCodes, language: $language, input: {zone: $zone}) {\\n    hotels {\\n      _id: ctyhocn\\n      amenityIds\\n      brandCode\\n      ctyhocn\\n      currencyCode\\n      distance\\n      distanceFmt\\n      homeUrl\\n      homepageUrl\\n      name\\n      phoneNumber\\n      address {\\n        addressFmt\\n        addressLine1\\n        addressLine2\\n        city\\n        country\\n        countryName\\n        postalCode\\n        state\\n        stateName\\n        __typename\\n      }\\n      coordinate {\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      thumbImage {\\n        hiResSrc(height: 430, width: 612)\\n        __typename\\n      }\\n      thumbnail: masterImage(variant: searchPropertyImageThumbnail) {\\n        altText\\n        variants {\\n          size\\n          url\\n          __typename\\n        }\\n        __typename\\n      }\\n      leadRate {\\n        lowest {\\n          rateAmount(currencyCode: $currencyCode, decimal: 0, strategy: trunc)\\n          rateAmountFmt(decimal: 0, strategy: trunc)\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"}"
        json_data = session.post(url, data=payload, headers=headers, params=querystring).json()
        # logger.info(json_data)
        k = (json_data['data']['hotelSummaryOptions']['hotels'])
        for j in k:
            if j['address']['country'] not in ("US","CA"):
                continue
            if j['brandCode'] not in ("QQ"):
                continue
            store = []
            store.append("https://curiocollection3.hilton.com")
            store.append(j['name'])
            store.append(j['address']['addressLine1'])
            store.append(j['address']['city'])
            store.append(j['address']['stateName'])
            store.append(j['address']['postalCode'])
            store.append(j['address']['country'])
            store.append("<MISSING>")
            store.append(j['phoneNumber'] if j['phoneNumber'] else "<MISSING>")
            store.append(j['brandCode'].replace("QQ","Curio Collection by Hilton"))
            store.append(j['coordinate']["latitude"])
            store.append(j['coordinate']["longitude"])
            # logger.info(j['coordinate']["longitude"])
            store.append("<MISSING>")
            store.append(j['homepageUrl'])
            if store[2] in address :
                continue
            address.append(store[2])
            yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
