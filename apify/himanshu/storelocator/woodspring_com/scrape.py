import csv
from datetime import datetime
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import unicodedata
import phonenumbers
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    main_url = "https://www.woodspring.com"
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    }
    r = session.get("https://www-api.woodspring.com/v1/gateway/hotel/hotels",headers=headers).json()["searchResults"]
    for store_data in r:
        store = []
        store.append(main_url)
        store.append(store_data["hotelName"])
        location_request = session.get("https://www-api.woodspring.com/v1/gateway/hotel/hotels/" + str(store_data["hotelId"]) + "?include=location,phones,amenities,contacts,occupancy,policies,rooms",headers=headers)
        location_data = location_request.json()
        if "hotelStatus" in location_data["hotelInfo"]["hotelSummary"]:
            if location_data["hotelInfo"]["hotelSummary"]['hotelStatus'] == "Closed":
                continue
        add = location_data["hotelInfo"]["hotelSummary"]["addresses"][0]
        try:
            phone = phonenumbers.format_number(phonenumbers.parse(str(location_data["hotelInfo"]["hotelSummary"]["phones"][1]["countryAccessCode"]+location_data["hotelInfo"]["hotelSummary"]["phones"][1]["areaCode"] + location_data["hotelInfo"]["hotelSummary"]["phones"][1]["number"]), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
        except:
            phone = phonenumbers.format_number(phonenumbers.parse(str(location_data["hotelInfo"]["hotelSummary"]["phones"][-1]["number"] ), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
        store.append(",".join(add["street"]))
        if store[-1] in addresses:
            continue
        addresses.append(store[-1])
        store.append(add["cityName"] if add["cityName"] else "<MISSING>")
        if "," + store[-1] + "," in store[2]:
            store[2] = store[2].split("," + store[-1])[0]
        store.append(add["subdivisionCode"] if add["subdivisionCode"] else "<MISSING>")
        store.append(add["postalCode"] if add["postalCode"] else "<MISSING>")
        store.append(add["countryCode"])
        store.append("<MISSING>")
        store.append(phone.replace("111111111","(863) 578-3658").replace("13213681","<MISSING>"))
        store.append("<MISSING>")
        store.append(location_data["hotelInfo"]["hotelSummary"]["geographicLocation"]["latitude"])
        store.append(location_data["hotelInfo"]["hotelSummary"]["geographicLocation"]["longitude"])
        # print("https://www.woodspring.com/" + str(store_data["hotelUri"]))
        if 'policyCodes' in location_data['hotelInfo']:
            if location_data['hotelInfo']['policyCodes']!= []:
                store.append(location_data['hotelInfo']['policyCodes'][0]['policyDescription'][0].replace("Hotel Office Hours :","").replace("|","").strip())
            else:
                store.append("<MISSING>")
        else:
            if "entireDay" in location_data["hotelInfo"]["hotelSummary"]['hotelAmenities'][-1]['hoursOfOperation']['mon'][0]:
                store.append("Daily 24 Hours")
            else:
                daily = {'mon':'Mon','tue':'Tue','wed':'Wed','thu':'Thu','fri':'Fri','sat':'Sat','sun':'Sun'}
                hours = ''
                hour = location_data["hotelInfo"]["hotelSummary"]['hotelAmenities'][-1]['hoursOfOperation']
                for day in hour:
                    hours+= daily[day] +" "+  datetime.strptime(hour[day][0]['startTime'], "%H:%M").strftime("%I:%M %p") +"-"+ datetime.strptime(hour[day][0]['endTime'], "%H:%M").strftime("%I:%M %p") + " "    
                store.append(hours.strip())
        store.append("https://www.woodspring.com/" + str(store_data["hotelUri"]))
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        # print(store)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
