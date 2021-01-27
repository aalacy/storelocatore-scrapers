import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kevajuice_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }

    base_url = "http://kevajuice.com/"

    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = "<MISSING>"
    phone = ""
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = ""

    r = session.get("http://www.kevajuicesw.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for loc in soup.find_all("div", class_="x-content-band man"):
        for loc1 in loc.find_all("div", class_="one-third"):
            try:
                page_url = "http://www.kevajuicesw.com/locations/"
                location_name = loc1.find("p", class_="stores").text.strip()
                store_number = location_name.split("#")[1].split()[0]
                address = list(
                    loc1.find("p", class_="stores").find_next("p").stripped_strings
                )
                if "(Near Food Court)" in address[0]:
                    del address[0]
                street_address = address[0].strip()
                if "201 Third St. NW" == street_address:
                    street_address = street_address + " " + "Suite D"
                if len(address) > 1:
                    city = address[1].split(",")[-2].strip()

                    state = address[1].split(",")[-1].split()[0].strip()
                    us_zip_list = re.findall(
                        re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),
                        str(address[1].split(",")[-1]),
                    )
                    if us_zip_list:
                        zipp = us_zip_list[0]
                    else:
                        zipp = "<MISSING>"
                    pat = r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"

                    phone_list = re.findall(
                        re.compile(pat),
                        str(address[-1]),
                    )
                    if phone_list:
                        phone = phone_list[0]
                        if ")" in phone:
                            phone = "(" + phone_list[0]
                    else:
                        phone = list(
                            loc1.find("p", class_="stores")
                            .find_next("p")
                            .find_next("p")
                            .stripped_strings
                        )[0]
                else:
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zipp = "<MISSING>"
                    phone = "<MISSING>"
                hours_of_operation = (
                    " ".join(list(loc1.find_all("p")[-1].stripped_strings))
                    .replace("Hours", "")
                    .replace("(Drive Thru Only)", "")
                )

                store = []
                store.append(base_url)
                store.append(page_url)

                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(country_code)
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(hours_of_operation)
                store = [x.replace("–", "-") if type(x) == str else x for x in store]
                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                yield store
            except:
                pass
    list_store_url = []
    r = session.get("http://kevajuice.com/store-locator/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for script in soup.find_all("div", {"class": re.compile("tp-caption")}):
        list_store_url.append(script.find("a")["href"])
        list_store_url = list(dict.fromkeys(list_store_url))
    for store_url in list_store_url:
        if "nevada" not in store_url and "new-mexico" not in store_url:
            if "http://kevajuice.com/colorado/" in store_url:
                data_url = [
                    "https://keva-juice-broadmoor-towne-center.square.site/",
                    "https://keva-juice-university-village-colorado.square.site/",
                ]
                for i in data_url:
                    page_url = i
                    col_r = session.get(page_url, headers=headers)
                    col_soup = BeautifulSoup(col_r.text, "lxml")
                    json_data = (
                        str(col_soup).split("window.siteData = ")[1].split("]}}}}}}")[0]
                        + "]}}}}}}"
                    )
                    json_data = json_data.split('"syncedLocation":')[1].split(
                        ',"verticalsHidden":true,"actionButtonConfig"'
                    )[0]
                    jd = json.loads(json_data)
                    location_name = jd["business_name"]
                    street_address = jd["street"] + " " + jd["street2"]
                    city = jd["city"].replace("Colo Spgs", "Colorado Springs")
                    state = jd["region"]
                    zipp = jd["postal_code"]
                    country_code = jd["country_code"]
                    store_number = "<MISSING>"
                    phone = jd["phone"].replace("+1 ", "")
                    location_type = "<MISSING>"
                    latitude = jd["lat"]
                    longitude = jd["lng"]
                    hoo = []
                    for h in jd["hours"]:
                        weekday = h["day"] + ":" + h["time"]
                        hoo.append(weekday)
                    hours_of_operation = ",".join(hoo)

                    store = []
                    store.append(base_url)
                    store.append(page_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append(country_code)
                    store.append(store_number)
                    store.append(phone)
                    store.append(location_type)
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours_of_operation)

                    store = [
                        x.replace("–", "-") if type(x) == str else x for x in store
                    ]
                    if store[2] in addressess:
                        continue
                    addressess.append(store[2])
                    yield store
            else:
                r_store = session.get(store_url, headers=headers)
                soup_store = BeautifulSoup(r_store.text, "lxml")
                table = soup_store.find("table")
                for tr in table.find_all("tr")[1:]:
                    page_url = store_url
                    address = list(tr.find_all("td")[0].stripped_strings)
                    if address == []:
                        location_name = "<MISSING>"
                        street_address = "<MISSING>"
                        city = "<MISSING>"
                        state = "<MISSING>"
                        zipp = "<MISSING>"
                    if len(address) == 1:
                        location_name = address[0].strip()
                        street_address = "<MISSING>"
                        city = "<MISSING>"
                        state = "<MISSING>"
                        zipp = "<MISSING>"
                    if len(address) == 3:
                        location_name = address[0].strip()
                        street_address = " ".join(address[1:-1]).strip()
                        city = address[-1].split(",")[0].strip()
                        state = (
                            address[-1]
                            .split(",")[-1]
                            .split()[0]
                            .strip()
                            .replace("Texas", "TX")
                        )
                        zipp = address[-1].split(",")[-1].split()[-1].strip()
                    if "Lubbock Keva" == location_name.strip():
                        page_url = "https://www.kevajuicelubbock.com/"
                    if "http://kevajuice.com/utah/" == page_url:
                        page_url = "https://www.kevajuiceutah.com/"
                    hours_of_operation = (
                        " ".join(list(tr.find_all("td")[1].stripped_strings))
                        .strip()
                        .replace("Follows Airport Hours", "")
                        .replace("Follows Mall Hours ", "")
                        .replace("May vary", "")
                        .strip()
                    )
                    phone_list = list(tr.find_all("td")[2].stripped_strings)
                    if "Store Website" in " ".join(phone_list):
                        phone_list.remove("Store Website")
                    if phone_list:
                        phone = phone_list[0]
                    else:
                        phone = "<MISSING>"
                    try:
                        coord = tr.find_all("td")[3].a["href"]

                        if "&sll" in coord:
                            latitude = coord.split("&sll=")[1].split(",")[0]
                            longitude = (
                                coord.split("&sll=")[1].split(",")[1].split("&")[0]
                            )
                        else:
                            latitude = "<MISSING>"
                            longitude = "<MISSING>"
                    except:
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                    store = []
                    store.append(base_url)
                    store.append(page_url)

                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append(country_code)
                    store.append("<MISSING>")
                    store.append(phone)
                    store.append(location_type)
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours_of_operation)
                    store = [
                        x.replace("–", "-") if type(x) == str else x for x in store
                    ]
                    if store[2] in addressess:
                        continue
                    addressess.append(store[2])
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
