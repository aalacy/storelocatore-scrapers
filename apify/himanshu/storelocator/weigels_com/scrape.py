import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_url = "https://weigels.com"
    r = session.get(base_url + "/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    main = soup.find_all(class_="location")
    for loc in main:
        lat = loc["data-lat"]
        lng = loc["data-lng"]
        name = loc.find("div", {"class": "locationInfo"}).find("h4").text.strip()
        storeno = (
            loc.find("div", {"class": "locationInfo"})
            .find("h4")
            .text.strip()
            .split("#")[-1]
        )
        madd = loc.find("h2", {"class": "locationAddress"}).text.strip().split(",")
        if "United States" in " ".join(madd):
            madd.remove(" United States")

        if len(madd) == 4:
            zipp_list = re.findall(
                re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str("".join(madd[1:]))
            )
            if zipp_list:
                zipp = zipp_list[0].strip()
            else:
                zipp = "<MISSING>"
            street_address = madd[0].strip()
            city = madd[1].strip()
            state_list = re.findall(r" ([A-Z]{2}) ", str(" ".join(madd[-2:])))
            if state_list:
                state = state_list[-1].strip()
            else:
                state = madd[-1].strip()

        elif len(madd) == 3:
            zipp_list = re.findall(
                re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str("".join(madd[1:]))
            )
            if zipp_list:
                zipp = zipp_list[0].strip()
            else:
                zipp = "<MISSING>"
            state = madd[-1].strip().split()[0]
            city = madd[-2].strip()
            street_address = madd[0].strip()
        elif len(madd) == 2:
            zipp_list = re.findall(
                re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str("".join(madd[1:]))
            )
            if zipp_list:
                zipp = zipp_list[0].strip()
            else:
                zipp = "<MISSING>"
            state = madd[-1].strip().split()[0]
            city = madd[0].split()[-1].strip()
            street_address = " ".join(madd[0].split()[:-1]).strip()

        else:
            zipp_list = re.findall(
                re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str("".join(madd))
            )
            if zipp_list:
                zipp = zipp_list[0].strip()
            else:
                zipp = "<MISSING>"
            street_address = " ".join(madd[0].split()[:-1]).strip()
            if madd[0].split()[-1].isdigit():
                city = "<MISSING>"
            else:
                city = madd[0].split()[-1].strip()

        street_address = (re.sub(" +", " ", street_address)).strip()
        try:
            phone = re.findall(r"[\d]{3}.[\d]{3}-[\d]{4}", str(loc.text))[0]
        except:
            phone = "<MISSING>"
        page_url = loc.find(class_="viewstore").a["href"]
        store = []
        store.append(base_url)
        store.append(name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(storeno)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(page_url)
        store = [x.replace("–", "-") if type(x) == str else x for x in store]
        store = [x.strip() if type(x) == str else x for x in store]
        store = [x if x else "<MISSING>" for x in store]
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
