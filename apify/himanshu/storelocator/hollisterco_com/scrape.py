import csv
import json
import lxml.html
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
import datetime

logger = SgLogSetup().get_logger("hollisterco_com")


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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

    base_url = "https://www.hollisterco.com"

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }

    requests = SgRequests()
    r = requests.get(
        "https://www.hollisterco.com/shop/ViewAllStoresDisplayView?storeId=19659&catalogId=11558&langId=-1",
        timeout=(30, 30),
        headers=headers,
    )
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("li", {"class": "view-all-stores__store"})
    for link in data:

        if (
            "/clothing-stores/CA/" in link.a["href"]
            or "/clothing-stores/US/" in link.a["href"]
            or "/clothing-stores/GB/" in link.a["href"]
        ):
            page_url = base_url + link.a["href"]
            logger.info(page_url)
            r = requests.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(r.text)
            soup = BeautifulSoup(r.text, "lxml")
            if "physicalStore" in r.text:
                json_data = json.loads(
                    r.text.split("try {digitalData.set('physicalStore',")[1].split(
                        ");}"
                    )[0]
                )
                location_name = json_data["name"]
                street_address = json_data["addressLine"][0]
                city = json_data["city"]
                state = json_data["stateOrProvinceName"]
                zipp = json_data["postalCode"]
                country_code = json_data["country"]
                store_number = json_data["storeNumber"]
                phone = json_data["telephone"]
                location_type = "<MISSING>"
                latitude = json_data["latitude"]
                longitude = json_data["longitude"]
                hours_of_operation = ""
                hours = store_sel.xpath('//li[@class="store-hours__row"]')
                hours_list = []
                year = str(datetime.datetime.now().year)
                for hour in hours:
                    date = "".join(
                        hour.xpath('span/span[@class="store-hours__col--date"]/text()')
                    ).strip()
                    date = year + "/" + date
                    day = datetime.datetime.strptime(date, "%Y/%m/%d").strftime("%A")
                    time = "".join(
                        hour.xpath('span[@class="store-hours__col--hours"]/text()')
                    ).strip()
                    hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()
                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"
                store = []
                store.append(base_url)
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
                store.append(page_url)
                yield store

        else:
            pass  # another country location


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
