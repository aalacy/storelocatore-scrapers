import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data.
    locator_domain = "https://www.insureone.com/"
    page_url = "<MISSING>"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "freewayinsurance"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = '<MISSING>'

    for zip_code in zips:
        try:
            page_no =1
            isFinish = False
            while isFinish is not True:
                form_data = "page="+str(page_no)+"&search=search&address="+str(zip_code)+"&radius=200"
                # r1 = "https://www.freewayinsurance.com/office-locator/?"+form_data
                # print(page_no,zip_code)
                r =requests.get("https://www.freewayinsurance.com/office-locator/?"+form_data,headers = headers)
                soup = BeautifulSoup(r.text,"lxml")
                loc= soup.find('article',class_ = "list").find("ul",class_ = "list")
                if list(loc.stripped_strings) == []:
                    isFinish = True
                    continue
                    # break
                else:
                    # print(page_no,zip_code)
                    # print(loc.prettify())
                    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    for x in loc.find_all('li'):
                    #     # print(x)
                        # location_name = x.find('h4').text.strip()
                        url = x.find('a',{'itemprop':'url'})['href']
                        #page redirect to the default page
                        if "freeway-insurance-milwaukee-wi-53215" == url.split('/')[-2]:
                            location_name = url.split('/')[-2]
                            address = x.find('div',{'itemprop':'address'})
                            list_add = list(address.stripped_strings)
                            street_address = "".join(list_add[0])
                            city = "".join(list_add[1])
                            state = "".join(list_add[2])
                            zipp = "".join(list_add[-1])
                            phone = x.find('span',{'itemprop':'telephone'}).text.strip()
                            latitude = "<MISSING>"
                            longitude = "<MISSING>"
                            hours_of_operation = "<MISSING>"
                            page_url = "<MISSING>"
                            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                                # store = ["<MISSING>" if x == "" or x ==
                                #          None else x for x in store]
                            store = [x if x else "<MISSING>" for x in store]
                            if store[2] in addresses:
                                    continue
                            addresses.append(store[2])
                            #print("data = " + str(store))
                            #print(
                                '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                            return_main_object.append(store)
                        else:



                            # print(location_name)
                            # print(url)
                            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


                            r_loc = requests.get(url,headers = headers)
                            # print(r_loc.text)
                            # print("~~~~~~~~~~~~~~~")
                            soup_loc = BeautifulSoup(r_loc.text,"lxml")
                            # print(soup_loc)
                            for sl in soup_loc.find_all('script',{'type':'application/ld+json'}):
                                # print(sl.contents)
                                oJson = json.loads(sl.text)
                                # print(oJson)
                                street_address = oJson['address']['streetAddress']
                                # print(zip_code+" | "+street_address) #53204
                                city = oJson['address']['addressLocality']
                                state = oJson['address']['addressRegion']
                                zipp = oJson['address']['postalCode']
                                phone =oJson['telephone']
                                page_url = oJson['url']
                                location_name ="".join(page_url).split('/')[-2]
                                # print(location_name) #87513
                                latitude = oJson['geo']['latitude']
                                longitude = oJson['geo']['longitude']
                                hours = oJson['openingHours']
                                hours_of_operation = " ".join(hours)

                                # print(hours_of_operation)
                                # print(street_address,city,state,zipp,latitude,longitude,hours_of_operation,url)
                                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                                store = [x if x else "<MISSING>" for x in store]

                                if store[2] in addresses:
                                    continue
                                addresses.append(store[2])

                                #print("data = " + str(store))
                                # #print(
                                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                                return_main_object.append(store)


                page_no +=1
        except:
            continue
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
