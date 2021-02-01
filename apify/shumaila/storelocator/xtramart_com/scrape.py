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
    url = "https://xtramart.com/wp-admin/admin-ajax.php?action=store_search&lat=43.96539&lng=-70.82265&max_results=100&search_radius=1000&autoload=1"
    loclist = session.get(url, headers=headers, verify=False).json()
    for loc in loclist:

        street = loc["address"] + " " + str(loc["address2"])
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        phone = loc["phone"]
        store = loc["id"]
        title = loc["store"].replace("&#8211;", "-")
        lat = loc["lat"]
        longt = loc["lng"]
        hours = loc["hours"]
        link = loc["permalink"]
        hours = (
            BeautifulSoup(hours, "html.parser")
            .find("table")
            .text.replace("day", "day ")
            .replace("PM", "PM ")
            .replace(":00", ":00 ")
            .strip()
        )

        data.append(
            [
                "https://xtramart.com/",
                link,
                title.replace(" &#038;", " & "),
                street.strip(),
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
