import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://www.mercy.net/content/mercy/us/en.solrQueryhandler?q=*:*&solrsort=&latitude=42.331427&longitude=-83.0457538&start=0&rows=2000&locationType=&locationOfferings=&servicesOffered=&distance=9999&pagePath=%2Fsearch%2Flocation"
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)["docs"]:
        loc = "https://www.mercy.net" + item["id"]
        name = item["name"]
        ste = ""
        if " Suite" in name:
            ste = name.split(" Suite")[1]
        if " Ste" in name:
            ste = name.split(" Ste")[1]
        if " - " in name:
            name = name.split(" - ")[0]
        city = item["city"]
        hours = (
            item["hoursOfOperation"]
            .replace("\r", "")
            .replace("\n", "")
            .replace("\t", "")
            .replace("&#10;", " ")
        )
        state = item["state"]
        add = item["address"]
        if ste != "":
            add = add + " Suite" + ste
        lng = item["location_1_coordinate"]
        lat = item["location_0_coordinate"]
        phone = item["phone"]
        typ = "<MISSING>"
        if "marketSiteOfServiceType" in item:
            typ = ""
            typs = item["marketSiteOfServiceType"]
            for styp in typs:
                if typ == "":
                    typ = styp
                else:
                    typ = typ + "; " + styp
        store = item["sosID"]
        website = "mercy.net"
        zc = item["zipcode"]
        country = "US"
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        yield [
            website,
            loc,
            name,
            add,
            city,
            state,
            zc,
            country,
            store,
            phone,
            typ,
            lat,
            lng,
            hours,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
