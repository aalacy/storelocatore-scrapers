from bs4 import BeautifulSoup
import csv
import json
import re

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
    pattern = re.compile(r"\s\s+")
    url = "https://www.serviceking.com/locations?view=see-all"
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split('"geoPoints":', 1)[1].split("}]", 1)[0]
    loclist = loclist + "}]"
    loclist = json.loads(loclist)
    for loc in loclist:
        store = loc["nid"]
        title = loc["title"]
        street = loc["address"]
        city = loc["city"]
        city, state = city.split(", ", 1)
        pcode = loc["zip"]
        lat = loc["lat"]
        longt = loc["lng"]
        phone = loc["phone"]
        try:
            if len(phone) < 3:
                phone = "<MISSING>"
        except:
            phone = "<MISSING>"
        try:
            if pcode.strip().isdigit():
                ccode = "US"
            else:
                ccode = "CA"
        except:
            pcode = "<MISSING>"
            ccode = "US"
        link = "https://www.serviceking.com" + loc["alias"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        hours = soup.find("div", {"class": "location-dtls__phones"}).text
        hours = re.sub(pattern, " ", hours).strip().replace("\n", " ")
        data.append(
            [
                "https://www.serviceking.com",
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
