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

    data = []

    url = "https://www.beggarspizza.com/wp-admin/admin-ajax.php?action=store_search&lat=41.87811&lng=-87.6298&max_results=50&search_radius=1000&autoload=1"
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()
    for loc in loclist:
        title = loc["store"]
        store = loc["id"]
        lat = loc["lat"]
        longt = loc["lng"]
        street = loc["address"] + " " + str(loc["address2"])
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        ccode = loc["country"]

        if ccode.find("United") > -1:
            ccode = "US"
        phone = loc["phone"]
        link = loc["permalink"]
        phone = loc["phone"]
        try:
            hours = (
                BeautifulSoup(loc["hours"], "html.parser")
                .find("table")
                .text.replace("PM", "PM ")
                .replace("day", "day ")
            )
        except:
            hours = "<MISSING>"
        title = title.encode("ascii", "ignore").decode("ascii")
        if len(phone) < 3:
            phone = "<MISSING>"
        if "-coming-soon" in link:
            continue
        data.append(
            [
                "https://www.beggarspizza.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
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
