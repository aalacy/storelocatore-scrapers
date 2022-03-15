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

    data = []

    url = "https://www.coasthotels.com/places-to-stay"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select('a:contains("View Hotel Website")')

    p = 0
    for link in linklist:
        link = link["href"]
        r = session.get(link, headers=headers, verify=False)
        loc = r.text.split('<script type="application/ld+json">')[-1].split(
            "</script", 1
        )[0]
        loc = json.loads(loc)
        title = loc["name"]
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        state = loc["address"]["addressRegion"]
        pcode = loc["address"]["postalCode"]
        ccode = loc["address"]["addressCountry"]
        if "Canada" in ccode:
            ccode = "CA"
        elif "United" in ccode:
            ccode = "US"
        try:
            lat, longt = loc["hasMap"].split("uery=", 1)[1].split(", ", 1)
        except:
            lat = longt = "<MISSING>"
        phone = loc["telephone"]

        data.append(
            [
                "https://www.coasthotels.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                longt,
                "<MISSING>",
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
