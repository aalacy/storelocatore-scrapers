import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup
import lxml.html

logger = SgLogSetup().get_logger("genesishealth_com")


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

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
    base_url = "https://www.genesishealth.com"
    r = session.get(
        "https://www.genesishealth.com/facilities/location-search-results/",
        headers=headers,
    )
    soup = BeautifulSoup(r.text, "lxml")

    for page in soup.find("div", {"class": "Pagination"}).find_all("option"):
        r1 = session.get(page["value"].replace("~", base_url))
        soup1 = BeautifulSoup(r1.text, "lxml")
        for script in soup1.find("div", {"class": "LocationsList"}).find_all("li"):

            location_name = script.find("a")["title"]
            addr = list(script.find("p", {"class": "TheAddress"}).stripped_strings)
            if len(addr[:-1]) == 1:
                street_address = " ".join(addr[:-1])
            else:

                number = re.findall(r"[0-9]{4}|[0-9]{3}", addr[0])
                if number:
                    street_address = addr[0]
                else:
                    street_address = addr[1]
            city = addr[-1].split(",")[0]
            state = addr[-1].split(",")[1].split(" ")[1]
            if len(addr[-1].split(",")[1].split(" ")) == 3:
                zipp = addr[-1].split(",")[1].split(" ")[-1]
            else:
                zipp = "<MISSING>"
            try:
                phone = script.find("span", {"class": "Phone"}).text
            except:
                phone = "<MISSING>"

            url = script.find("a")["href"].replace("../", "").replace("amp;", "")
            if "http" in url:
                page_url = url
            elif "location-public-profile" in url:
                page_url = "https://www.genesishealth.com/facilities/" + url
            else:
                page_url = "https://www.genesishealth.com/" + url
            if "&id" in url:
                store_number = page_url.split("&id=")[-1]
            else:
                store_number = "<MISSING>"

            lat = "<MISSING>"
            lng = "<MISSING>"
            hours = "<MISSING>"
            if "genesishealth.com" in page_url:

                logger.info(page_url)
                store_req = session.get(page_url)
                store_sel = lxml.html.fromstring(store_req.text)
                location_soup = BeautifulSoup(store_req.text, "lxml")
                coords = location_soup.find("script", {"type": "application/ld+json"})
                if coords:
                    try:
                        lat = str(coords).split('"latitude": "')[1].split('"')[0]
                        lng = str(coords).split('"longitude": "')[1].split('"')[0]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    location_type = str(coords).split('"@type": "')[1].split('"')[0]
                else:
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    location_type = "<MISSING>"

                temp_hours = store_sel.xpath("//div[@class='DaySchedule ClearFix']")
                hours_list = []
                hours = ""
                for hour in temp_hours:
                    day = "".join(hour.xpath('div[@class="Day"]/text()')).strip()
                    time = "".join(hour.xpath('div[@class="Times"]/text()')).strip()
                    hours_list.append(day + time)

                hours = "; ".join(hours_list).strip()
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address.replace("Floor", "").replace("floor", ""))
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)

            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
