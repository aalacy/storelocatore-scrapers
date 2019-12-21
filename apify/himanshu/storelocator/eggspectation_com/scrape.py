import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    base_url = "https://eggspectation.com"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("div", {"class": "fw-text-inner"})
    hours = []
    name_store = []
    store_detail = []
    phone = []
    store_name = []
    st = []
    city = []
    state = []
    zip1 = []
    contry = []
    page_url = []
    return_main_object = []

    longitude = []
    latitude = []
    for i in range(2, 4):
        k = (soup.find("div", {"class": "et_pb_button_module_wrapper et_pb_button_" + str(
            i) + "_wrapper et_pb_button_alignment_center et_pb_module"}).a['href'])

        r = requests.get(k, headers=headers)
        soup1 = BeautifulSoup(r.text, "lxml")
        k1 = (soup1.find_all("div", {"class": "et_pb_text_inner"}))
        lat = soup1.find_all("div", {"class": "et_pb_button_module_wrapper"})
        for i in lat:
            if "DETAILS" in i.text:
                r = requests.get(i.a['href'], headers=headers)
                soup3 = BeautifulSoup(r.text, "lxml")
                latitude1 = (soup3.find("iframe")['src'].split("1d"))
                # print(latitude1)
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
                if len(latitude1) == 2:
                    latitude.append(latitude1[-1].split("!2d")[0])
                    longitude.append(
                        latitude1[-1].split("!2d")[1].split("!3")[0])
                else:
                    try:
                        r_coord = requests.get(soup3.find("iframe")[
                                               'src'], headers=headers)
                        soup_coord = BeautifulSoup(r_coord.text, 'lxml')
                        script = soup_coord.find(lambda tag: (
                            tag.name == "script") and "initEmbed" in tag.text)
                        sc_string = script.text.split(
                            'initEmbed(')[1].split(');')[0].split(',')[156:160]
                        if ' Canada"' in " ".join(sc_string):
                            sc_string.remove(' Canada"')
                        if sc_string == []:
                            latitude.append("<MISSING>")
                            longitude.append("<MISSING>")
                        else:
                            coord_list = " ".join(sc_string).split(
                                '[')[1].split(']')[0].split()
                            if len(coord_list) > 1:
                                latitude.append(coord_list[0])
                                longitude.append(coord_list[1])
                            else:
                                sc_string = script.text.split(
                                    'initEmbed(')[1].split(');')[0].split(',')[46:48]
                                latitude.append(sc_string.split(',')[0])
                                longitude.append(sc_string.split(',')[
                                                 1].replace(']', ''))

                    except:
                        # pass
                        sc_string = script.text.split(
                            'initEmbed(')[1].split(');')[0].split(',')[124:126]
                        # list_coord = [list((i, sc_string[i]))
                        #               for i in range(len(sc_string))]
                        latitude.append(sc_string[-1].replace(']', ''))
                        longitude.append(sc_string[0])

        for j in k1:
            tem_var = []
            zip2 = ''
            if j.p.find("span", {"style": "font-family: oswald-bold; font-size: 18pt; color: #000000;"}) != None:
                store_name.append(j.p.find("span", {
                                  "style": "font-family: oswald-bold; font-size: 18pt; color: #000000;"}).text)

            p = j.find('p')
            if len(list(j.find_all('p')[-1].stripped_strings)) != 1:
                if list(j.find_all('p')[-1].stripped_strings) != []:
                    hours.append(" ".join(list(j.find_all('p')[-1].stripped_strings)).replace(
                        "Hours:", "").replace("HAPPY HOUR:", "").replace("Boozy Brunch Drinks:", ""))

            if len(list(p.stripped_strings)) != 1:
                phone.append(list(p.stripped_strings)
                             [-1].replace("Phone: ", ""))

                st1 = list(p.stripped_strings)[:-2]
                if len(st1) == 2 or st1[0] == "Eggspectation Carlton (Opening Soon)" or st1[0] == "Bell Trinity" or st1[0] == "Eggspectation Vaughan (Opening Soon)" or st1[0] == "Woodbridge Square":
                    del st1[0]

                st.append(" ".join(st1).replace("Woodbridge Square", ""))

                l = list(p.stripped_strings)[-2].replace(".", ",").split(',')
                # if "Ont" in " ".join(l):
                #     print(l)
                if len(l) == 3:
                    city.append(l[0])
                    if "Ont" == l[1].strip():
                        l[1] = "Ontario"
                    # print(l[1])
                    state.append(l[1])
                    zip1.append(l[-1])
                    zip2 = l[-1]

                else:
                    city.append(l[0])
                    state.append(l[1].split()[0])
                    zip2 = " ".join(l[1].split()[1:])
                    zip1.append(" ".join(l[1].split()[1:]))

                if len(zip2) != 5:
                    contry.append("CA")
                    page_url.append(k)
                else:
                    contry.append("US")
                    page_url.append(k)

    hours.insert(0, "<MISSING>")
    hours.insert(1, "<MISSING>")
    hours.insert(4, "Monday – Sunday: 6:30 am – 9:30pm")

    latitude.insert(0, "<MISSING>")
    latitude.insert(1, "<MISSING>")
    longitude.insert(0, "<MISSING>")
    longitude.insert(1, "<MISSING>")
    for i in range(len(store_name)):
        store = list()
        store.append("https://eggspectation.com")
        store.append(store_name[i] if store_name[i] else "<MISSING>")
        store.append(st[i] if st[i] else "<MISSING>")
        store.append(city[i])
        store.append(state[i])
        store.append(zip1[i])
        store.append(contry[i])
        store.append("<MISSING>")
        store.append(phone[i].replace("TBA", "<MISSING>"))
        store.append("<MISSING>")
        store.append(latitude[i])
        store.append(longitude[i])

        store.append(hours[i].replace(" TBA", "<MISSING>"))
        store.append(page_url[i])
        if "45 Carlton Street Unit 200" in store or " 7600 Weston Road, Unit 70C" in store:
            pass
        else:
            store = [str(x).encode('ascii', 'ignore').decode(
                'ascii').strip() if x else "<MISSING>" for x in store]
            if "Qubec" == store[4]:
                store[4] = "Quebec"
            #print("data ==" + str(store))
            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
