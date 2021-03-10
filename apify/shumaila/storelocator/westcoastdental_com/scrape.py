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
    url = "https://www.westcoastdental.com"
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split('<script type="application/ld+json">', 1)[1].split(
        "</script", 1
    )[0]
    loclist = re.sub(pattern, "", loclist).strip()
    loclist = json.loads(loclist)
    loclist = loclist["@graph"][1:]
    for loc in loclist:
        title = loc["name"]
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        state = loc["address"]["addressRegion"]
        pcode = loc["address"]["postalCode"]
        phone = loc["address"]["telephone"][0]
        hours = " ".join(loc["openingHours"])
        lat = loc["geo"]["latitude"]
        longt = loc["geo"]["longitude"]
        link = loc["url"]

        data.append(
            [
                "https://westcoastdental.com",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
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
