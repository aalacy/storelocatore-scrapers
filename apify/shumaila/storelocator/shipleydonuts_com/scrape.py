from bs4 import BeautifulSoup
import csv
import json
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
    url = "https://shipleydonuts.com/stores-html-sitemap/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=stores]")
    for link in linklist:
        link = link["href"]
        if "sitemap" not in link:
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            content = r.text.split('"locations":', 1)[1].split("};", 1)[0]
            content = json.loads(content)
            content = content[0]
            title = content["store"]
            phone = soup.select_one("a[href*=tel]").text
            street = content["address"] + " " + content["address2"]
            city = content["city"]
            state = content["state"]
            pcode = content["zip"]
            ccode = "US"
            lat = content["lat"]
            longt = content["lng"]
            try:
                hours = (
                    soup.find("table", {"class": "wpsl-opening-hours"})
                    .text.replace("day", "day ")
                    .replace("PM", "PM ")
                )
            except:
                hours = "<MISSING>"
            store = content["id"]
            data.append(
                [
                    "https://shipleydonuts.com/",
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
