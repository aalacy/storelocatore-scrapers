import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
        return_main_object = []
        name_store = []
        store_detail = []
        base_url = "https://www.shinola.com/store-locator"
        r = requests.get(base_url)
        soup = BeautifulSoup(r.text, "lxml")

        vk = soup.find('div', {'id': 'amazon-root'}).find_next('script').find_next('script').text.split('"stores":')[1].split(',"total"')[0]
        addresses = []
        k = json.loads(vk)

        main = {}
        # JArray = []
        for idx, val in enumerate(k):
            main[val["name"]] = [val['latitude'], val['longtitude']]

        for loop in range(0, 20):
            base_url = "https://www.shinola.com/shinstorelocator/index/searchlocation/?location=&shinolaStoresCurrentPage=0&authorizedRetailersCurrentPage="+str(loop)
            r = requests.get(base_url)
            soup = BeautifulSoup(r.text, "lxml")

            k = json.loads(soup.text)

            for idx, val in enumerate(k['shinola_stores']):
                tem_var = []
                lat = "<MISSING>"
                lng = "<MISSING>"
                name_store = val["name"].strip()

                for b in main:
                    if b == name_store:
                        lat = main[b][0]

                        lng = main[b][1]



                zipcode = (val['postcode'])
                phone = ''
                if val['phone'] == []:
                    phone = val['phone']



                street = val['street']
                city = val['city']
                country = val['country']
                state = val['region']
                hours = 'monday' + ' ' + val['monday_open'] + ' ' + val['monday_close'] + ' ' + 'tuesday' + ' ' + val[
                    'tuesday_open'] + ' ' + val['tuesday_close'] + ' ' + ' wednesday' + ' ' + val[
                            'wednesday_open'] + ' ' + val['wednesday_close'] + ' ' + ' thursday' + ' ' + val[
                            'thursday_open'] + ' ' + val['thursday_close'] + ' ' + 'friday' + ' ' + val[
                            'friday_open'] + ' ' + val['friday_close'] + ' ' + 'saturday' + ' ' + val[
                            'saturday_open'] + ' ' + val['saturday_close'] + ' ' + 'sunday' + ' ' + val[
                            'sunday_open'] + ' ' + val['sunday_close']

                if street in addresses:
                    continue
                addresses.append(street)
                tem_var.append(name_store if name_store else "<MISSING>")
                tem_var.append(street if street else "<MISSING>")
                tem_var.append(city if city else "<MISSING>")
                tem_var.append(state if state else "<MISSING>")
                tem_var.append(zipcode if zipcode else "<MISSING>")
                tem_var.append(country if country else "<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(phone if phone else "<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(lat)
                tem_var.append(lng)
                tem_var.append(hours)
                tem_var.append("https://www.shinola.com/shinstorelocator/index/searchlocation/?location=&shinolaStoresCurrentPage=0&authorizedRetailersCurrentPage="+str(loop))
                store_detail.append(tem_var)



            for idx, val in enumerate(k['authorized_retailers']):
                tem_var = []
                # zipcode=''

                lat = "<MISSING>"
                lng = "<MISSING>"

                name_store = val["name"].strip()

                for b in main:
                    if b == name_store:
                        lat = main[b][0]

                        lng = main[b][1]
                zipcode1 = val['postcode']
                # print(len(zipcode))
                phone = ''
                if val['phone'] == []:
                    phone = val['phone']
                street = val['street']
                city = val['city']
                country = val['country']
                state = val['region']
                tem_var.append(name_store if name_store else "<MISSING>")
                if "40 Monroe Center #103" in street:
                    street = (street.replace("40 Monroe Center #103", "103 Monroe Center"))

                if "Somerset Collection" in street:

                    street = city.split('.')[0]
                    city = city.split('.')[1]

                    tem_var.append(street if street else "<MISSING>")
                    tem_var.append(city if city else "<MISSING>")
                else:
                    tem_var.append(street if street else "<MISSING>")
                    tem_var.append(city if city else "<MISSING>")

                if zipcode1:
                    if len(zipcode1) == 4:
                        zipcode = str(0) + zipcode1
                    else:
                        zipcode = zipcode1

                if street in addresses:
                    continue
                addresses.append(street)
                tem_var.append(state if state else "<MISSING>")
                tem_var.append(zipcode.replace("Mati", "").replace("24B", "<MISSING>").replace("918",
                                                                                               "<MISSING>") if zipcode else "<MISSING>")
                tem_var.append(country if country else "<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(phone.replace(", (905) 4", "").replace("(0155) 5518 1313", "") if phone else "<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(lat)
                tem_var.append(lng)
                tem_var.append("<MISSING>")
                tem_var.append("https://www.shinola.com/shinstorelocator/index/searchlocation/?location=&shinolaStoresCurrentPage=0&authorizedRetailersCurrentPage="+str(loop))

                store_detail.append(tem_var)




        for i in range(len(store_detail)):

            store = list()
            store.append("https://www.shinola.com")
            store.extend(store_detail[i])
            # print('data====',str(store))
            yield store



def scrape():
    data = fetch_data()
    write_output(data)


scrape()


