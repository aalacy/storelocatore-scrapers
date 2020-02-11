import csv
import requests
from bs4 import BeautifulSoup
import re
import io
import json


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.facelogicspa.com/pages/spas"
    r = requests.get(base_url, headers=headers)
    addressess =[]
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.select('.pt25.pl25.pr25.pb25')
    for links in exists[0].findAll('a'):
        if "http" in links.get('href'):
            detail_page_url = links.get('href')
            # print(links.get('href'))
            if "Clovis" in links.get('href'):

                contact_url_details = requests.get(
                    "http://www.facelogicclovis.com/pages/contact", headers=headers)
                contact_url_soup = BeautifulSoup(
                    contact_url_details.text, "lxml")
                page_url = "http://www.facelogicclovis.com/pages/contact"
                address = contact_url_soup.find('h1').parent.get_text(
                ).replace("\n", ' ').strip().split(',')
                location_name = address[0].split(' ')[-1]
                street_address = address[1].strip() + address[2].strip()
                city = links.get_text()
                state = address[-1].strip().split('.')[0].split(' ')[0]
                zip = address[-1].strip().split('.')[0].split(' ')[1]
                phone = address[-1].strip().split('.')[1].strip()[:-1]
                hours_of_operation = "<MISSING>"
            elif "facelogicbroomfield" in links.get('href'):
                
                # print("~~~~~~~~~~~~~~~~~ ",links.get('href'))
                contact_url_details = requests.get(
                    "http://www.facelogicbroomfield.com/facelogicco/ContactUs", headers=headers)
                page_url = "http://www.facelogicbroomfield.com/facelogicco/ContactUs"
                contact_url_soup = BeautifulSoup(
                    contact_url_details.text, "lxml")
                address = contact_url_soup.select(
                    '.row-1')[0].findAll('p')[-1].get_text().split(',')
                location_name = "Facelogic Essential Skincare Spa"
                street_address = ' '.join(address[:-1])[9:]
                city = links.get_text()
                state = address[-1].strip().split(' ')[0]
                zip = address[-1].strip().split(' ')[1]
                phone = contact_url_soup.select(
                    '.row-1')[0].findAll('p')[-3].get_text()[7:]
                hours_of_operation = contact_url_soup.select('.content')[1].find('h2').find_next('p').get_text()+" , "+contact_url_soup.select('.content')[1].find('h2').find_next('p').find_next('p').get_text()+" , "+ contact_url_soup.select('.content')[1] \
                .find('h2').find_next('p').find_next('p').find_next('p').get_text()+" , "+contact_url_soup.select('.content')[1].find('h2').find_next('p').find_next('p').find_next('p').find_next('p').get_text() \
                +" , "+contact_url_soup.select('.content')[1].find('h2').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text()   \
                +" , "+contact_url_soup.select('.content')[1].find('h2').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text() \
                +" , "+contact_url_soup.select('.content')[1].find('h2').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text()
                print(hours_of_operation)
                # .find_next('p').find_next('p').get_text() + ", " + contact_url_soup.select('.content')[1].find('h2').find_next(
                #     'p').find_next('p').find_next('p').get_text() + ", " + contact_url_soup.select('.content')[1].find('h2').find_next('p').find_next('p').find_next('p').find_next('p').get_text()
            
            elif "facelogicsc" in links.get('href'):
                
                contact_url_details = requests.get("https://facelogicsc.com", headers=headers)
                contact_url_soup = BeautifulSoup(
                    contact_url_details.text, "lxml")
                page_url = "https://facelogicsc.com"
                location_name = "Hautigo Spa"
                address = contact_url_soup.findAll("div",{"class":"textwidget"})
                # 'h3')[-1].find_next('p').get_text().replace("\n", ' ').split(',')
                hours_of_operation = " ".join(list(address[1].stripped_strings)).split(".menu")[0]
                # print(" ".join(list(address[1].stripped_strings)).split(".menu")[0])
                phone = list(address[-1].stripped_strings)[1]
                city = list(address[-1].stripped_strings)[-1].split(",")[0]
                zip = list(address[-1].stripped_strings)[-1].split(",")[1].strip().split(" ")[-1]
                state = list(address[-1].stripped_strings)[-1].split(",")[1].strip().split(" ")[0]
                
                # 
                # street_address = address[0].strip()
                # city = links.get_text()
                # state = address[1].strip().split(' ')[0]
                # zip = address[1].strip().split(' ')[1]
                # phone = contact_url_soup.select(
                #     '#text-8')[0].find('a').get_text()
                hours_of_operation = contact_url_soup.select(
                    '#text-7')[0].find('ul', {'class', 'menu'}).get_text().replace('\n', ' ').strip()
            elif "facelogickisco" in links.get('href'):
                # print("~~~~~~~vv~~~~~~~~~~ ",links.get('href'))

                contact_url_details = requests.get(
                    "https://facelogickisco.com/contact-find-us/", headers=headers)
                page_url = "https://facelogickisco.com/contact-find-us/" 
                contact_url_soup = BeautifulSoup(
                    contact_url_details.text, "lxml")
                address = contact_url_soup.select(
                    '.entry-content')[0].findAll('p')[-2].get_text().replace("\n", ',').split(',')

                location_name = "MT. KISCO, NEW YORK"
                street_address = address[0].strip() + " " + address[1].strip()
                city = links.get_text()
                state = address[-3].strip().split(' ')[0]
                zip = address[-3].strip().split(' ')[1]
                phone = address[-2][7:]
                hours_of_operation = contact_url_soup.select(
                    '.textwidget.custom-html-widget')[0].get_text().replace('\n', ' ').strip()
                # print(hours_of_operation)
            elif "facelogicbcs" in links.get('href'):
                
                contact_url_details = requests.get(
                    "http://www.facelogicbcs.com/", headers=headers)
                page_url = "http://www.facelogicbcs.com/" 
                contact_url_soup = BeautifulSoup(
                    contact_url_details.text, "lxml")
                address = contact_url_soup.find('h3').get_text().split(',')
                location_name = "FacelogicBCS"
                street_address = ' '.join(address[:-1])
                # print(contact_url_soup.find("span",{"class":"site-phone"}).text)
                #print(street_address)
                city = links.get_text()
                state = address[-1].split(' ')[1]
                zip = address[-1].split(' ')[-1][1:]
                phone = contact_url_soup.find("span",{"class":"site-phone"}).text
                hours_of_operation = "<MISSING>"
            elif "facelogichighlandpark" in links.get('href'):
                # print("~~~~~~~done....~~~~~~~~~~ ",links.get('href'))
                contact_url_details = requests.get(
                    "https://facelogichighlandpark.com/contact-us", headers=headers)
                page_url = "https://facelogichighlandpark.com/contact-us"
                contact_url_soup = BeautifulSoup(
                    contact_url_details.text, "lxml")
                address = contact_url_soup.find('h4').find_next('h4').find_next(
                    'p').get_text().replace('\n', ',').split(',')
                # print("heeyyyy ",  address)
                location_name = contact_url_soup.find(
                    'h4').find_next('h4').get_text()
                street_address = ' '.join(address[:-2])
                city = links.get_text()
                state = address[-2].strip().split(' ')[0]
                zip = address[-2].strip().split(' ')[1]
                phone = contact_url_soup.find('h4').find_next(
                    'h4').find_next('p').find_next('p').find('a').get_text()
                hours_of_operation = contact_url_soup.findAll(
                    'h4')[-1].find_next('p').find_next('div').get_text().replace('\n', ' ')
            elif "salonvision" in links.get('href'):
                contact_url_details = requests.get(
                    "https://www.salonvision.com/facelogictx/", headers=headers)
                page_url = "https://www.salonvision.com/facelogictx/"
                contact_url_soup = BeautifulSoup(
                    contact_url_details.text, "lxml")
                address = contact_url_soup.select(
                    "#footerinfo")[0].get_text().replace("\r\n", '').split("|")
                location_name = "<MISSING>"
                street_address = address[0].replace("\n", '').split(
                    ',')[1].strip() + " " + address[1].strip().split(',')[0].strip()
                city = links.get_text()
                state = address[1].strip().split(
                    ',')[1].strip().split(' ')[0].strip()
                zip = address[1].strip().split(
                    ',')[1].strip().split(' ')[1].strip()
                phone = address[-1].strip()
                hours_of_operation = "<MISSING>"

            # elif "facelogicspawaco" in links.get('href'):
            else:
                contact_url_details = requests.get(
                    "https://facelogicspawaco.com/contact-us/", headers=headers)
                page_url = "https://facelogicspawaco.com/contact-us/"
                contact_url_soup = BeautifulSoup(
                    contact_url_details.text, "lxml")
                address = contact_url_soup.select(".et_pb_all_tabs")[0].select(
                    '.et_pb_tab_content')[0].get_text().replace("\n", '').split(',')
                location_name = "<MISSING>"
                street_address = address[0]
                city = links.get_text()
                state = address[1].strip().split(' ')[0]
                zip = address[1].strip().split(' ')[1]
                phone = contact_url_soup.select(".et_pb_all_tabs")[0].select(
                    '.et_pb_tab_content')[1].get_text().replace("\n", '').split("Email:")[0][14:]

                hours_of_operation = contact_url_soup.select(".et_pb_all_tabs")[0].select(
                    '.et_pb_tab_content')[2].get_text().replace('\n', ' ').strip().split(": CLOSED Note:")[0]
        else:
            detail_page_url = "http://www.facelogicspa.com" + links.get('href')
            detail_url = requests.get(
                "http://www.facelogicspa.com" + links.get('href'), headers=headers)
            page_url = "http://www.facelogicspa.com" + links.get('href')
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            address = detail_soup.select('.mt20.mb20')[0].find('p').get_text().replace(
                '\r\n', '').strip().replace("         ", '').split(',')
            location_name = "<MISSING>"
            street_address = ''.join(address[:-1])
            city = links.get_text()
            state = address[-1].strip().split(' ')[0]
            zip = address[-1].strip().split(' ')[1]
            phone = (detail_soup.select('.mt20.mb20')[0].find(
                'p').next_sibling.strip()[3:]).replace('FACE ', '')
            hours_of_operation = "<MISSING>"

        street_address = street_address.replace(u'\xa0', u' ').replace("Chino Hills", "").replace("Tustin", "").replace("Broomfield", "").replace(
            "Roswell", "").replace("Las Vegas", "").replace("|  College Station", "").replace("Dallas", "").replace(" San Antonio", "").strip()
        city = city.split("-")[0].strip()
        # print(street_address)
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        store = []
        store.append('http://www.facelogicspa.com/')
        store.append(location_name)
        store.append(street_address.replace('Mt. Kisco',''))
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours_of_operation.encode('ascii', 'ignore').decode('ascii').strip())
        store.append(page_url)
        # print(store)
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
