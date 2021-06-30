from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
    p = 0
    data = []
    url = "https://www.pizzapatron.com/wp-admin/admin-ajax.php?action=store_search&lat=30.26715&lng=-97.74306&max_results=25&search_radius=25&autoload=1"
    loclist = session.get(url, headers=headers, verify=False).json()
    for loc in loclist:
        street = loc["address"]
        store = loc["id"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        lat = loc["lat"]
        longt = loc["lng"]
        hours = (
            BeautifulSoup(loc["hours"], "html.parser")
            .text.replace("PM", "PM ")
            .replace("day", "day ")
        )
        link = loc["url"]
        phone = loc["phone"]
        if len(state) < 3:
            state = "TX"
        if "Texas" in state:
            state = "TX"
        data.append(
            [
                "https://www.pizzapatron.com/",
                link,
                street,
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

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
