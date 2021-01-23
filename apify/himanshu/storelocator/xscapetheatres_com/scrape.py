import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("xscapetheatres_com")
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.xscapetheatres.com/showtimes"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("div", {"class": "set-house-inner"})
    for i in data:
        final_data = i.find_all("div", {"class": "item-column-name"})
        for j in final_data:
            mp = list(j.stripped_strings)
            location_name = mp[0]
            street_address = mp[1]
            city = mp[2].split(",")[0]
            state = mp[2].split(",")[1].split(" ")[1]
            store_zip = mp[2].split(",")[1].split(" ")[-1]
            return_object = []
            return_object.append("https://www.xscapetheatres.com/")
            return_object.append(location_name)
            return_object.append(street_address.replace(",", ""))
            return_object.append(city)
            return_object.append(state)
            return_object.append(store_zip)
            return_object.append("US")
            return_object.append("<MISSING>")
            return_object.append("<MISSING>")
            return_object.append("xscape theatres")
            return_object.append("<MISSING>")
            return_object.append("<MISSING>")
            return_object.append("<MISSING>")
            return_object.append("<INACCESSIBLE>")
            yield return_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
