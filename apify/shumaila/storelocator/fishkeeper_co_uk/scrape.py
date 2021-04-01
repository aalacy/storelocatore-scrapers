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
    # Your scraper here
    data = []
    pattern = re.compile(r"\s\s+")
    url = "https://www.fishkeeper.co.uk/storefinder"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split(':{"stores":')[1].split(',"center"', 1)[0]
    r = r.replace("\n", "")
    loclist = json.loads(r)
    for loc in loclist:
        title = loc["title"]
        phone = loc["phone"]
        address = loc["address"]
        address = re.sub(pattern, "\n", address)
        pcode = address.split("\n")[-1]
        city = address.split("\n")[-2]
        street = " ".join(address.split("\n")[0:-2])
        state = loc["region"]
        lat = loc["lat"]
        longt = loc["lng"]
        link = loc["url"]
        store = loc["id"]
        hours = "<MISSING>"
        r = session.get(link, headers=headers, verify=False)
        hours = (
            BeautifulSoup(r.text, "html.parser")
            .find("div", {"class": "store-finder__main"})
            .find("div", {"class": "time"})
            .text.replace("\n", "")
        )
        try:
            hours = hours.split("-")[0]
        except:
            pass
        if "Due to" in hours:
            hours = "<MISSING>"
        if len(phone) < 3:
            phone = "<MISSING>"
        if len(pcode) < 2:
            pcode = city
            city = street.strip().split(" ")[-1]
        data.append(
            [
                "https://www.fishkeeper.co.uk/",
                link,
                title,
                street,
                city,
                state,
                pcode.replace("\xa0", ""),
                "UK",
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
