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
    # Your scraper here
    data = []
    url = "https://api-cdn.storepoint.co/v1/15f4fbe5b10e3d/locations?rq"
    r = session.get(url, headers=headers, verify=False)
    loclist = json.loads(r.text)
    loclist = loclist["results"]["locations"]

    for loc in loclist:
        title = loc["name"]
        store = loc["id"]
        lat = loc["loc_lat"]
        longt = loc["loc_long"]
        address = loc["streetaddress"].split(",")
        street = ",".join(address[:-3])
        city = address[-3].lstrip()
        state = " ".join(address[-2].split(" ")[:-2]).lstrip()
        pcode = address[-2].split(" ")[-2] + " " + address[-2].split(" ")[-1]
        ccode = address[-1].lstrip()
        store_type = loc["tags"]
        phone = loc["phone"]
        mon = loc["monday"]
        tues = loc["tuesday"]
        wed = loc["wednesday"]
        thurs = loc["thursday"]
        fri = loc["friday"]
        sat = loc["saturday"]
        sun = loc["sunday"]

        hours_of_operation = (
            "Mon: "
            + mon
            + ", Tues: "
            + tues
            + ", Wed: "
            + wed
            + ", Thurs: "
            + thurs
            + ", Fri: "
            + fri
            + ", Sat: "
            + sat
            + ", Sun: "
            + sun
        )
        if title == "":
            title = "<MISSING>"
        if store == "":
            store = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
        if longt == "":
            longt = "<MISSING>"
        if street == "":
            street = "<MISSING>"
        if city == "":
            city = "<MISSING>"
        if pcode == "":
            pcode = "<MISSING>"
        if ccode == "":
            ccode = "UK"
        if store_type == "":
            store_type = "<MISSING>"
        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"
        data.append(
            [
                "https://www.tofs.com/",
                "https://www.tofs.com/pages/store-finder",
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                store_type,
                lat,
                longt,
                hours_of_operation,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
