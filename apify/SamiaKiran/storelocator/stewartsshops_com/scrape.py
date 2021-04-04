import csv
import html
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("stewartsshops_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    # Your scraper here
    data = []
    urls = [
        "https://www.stewartsshops.com/wp-admin/admin-ajax.php?action=store_search&lat=44.5588&lng=-72.57784&max_results=&search_radius=200",
        "https://www.stewartsshops.com/wp-admin/admin-ajax.php?action=store_search&lat=42.70152&lng=-75.27124&max_results=300&search_radius=200",
    ]
    for url in urls:
        loclist = session.get(url, headers=headers, verify=False).json()

        for loc in loclist:
            title = loc["store"]
            if len(title) < 2:
                title = "<MISSING>"
            title = html.unescape(title)
            store = title.split("#", 1)[1].replace("-", "").lstrip()
            if store.split(" "):
                store = store.split(" ")[0]
            if len(store) < 2:
                store = "<MISSING>"
            street = loc["address"].replace("Watervliet NY 12189", "")
            if len(street) < 2:
                street = "<MISSING>"
            city = loc["city"]
            if len(city) < 2:
                city = "<MISSING>"
            state = loc["state"]
            if len(state) < 2:
                state = "<MISSING>"
            pcode = loc["zip"]
            if len(pcode) < 2:
                pcode = "<MISSING>"
            lat = loc["lat"]
            if len(lat) < 2:
                lat = "<MISSING>"
            longt = loc["lng"]
            if len(longt) < 2:
                longt = "<MISSING>"
            phone = loc["phone"]
            phone = phone.split("|", 1)[0]
            if len(phone) < 2:
                phone = "<MISSING>"
            hours_list = loc["hours"]
            if len(hours_list) < 2:
                hours = "<MISSING>"
            hours_list = BeautifulSoup(hours_list, "html.parser")
            hours_list = hours_list.findAll("tr")
            hours = ""
            for temp in hours_list:
                day = temp.find("td").text
                temp_hour = temp.find("time").text
                hours = hours + day + " " + temp_hour + " "
            data.append(
                [
                    "https://www.stewartsshops.com/",
                    "https://www.stewartsshops.com/find-a-shop/",
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours,
                ]
            )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
