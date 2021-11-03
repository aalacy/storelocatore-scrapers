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
    url = "https://www.surcheros.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split('<script type="application/ld+json">', 1)[1].split(
        "</script", 1
    )[0]
    loclist = json.loads(loclist)
    p = 0
    for loc in loclist["subOrganization"]:
        link = loc["url"]
        title = loc["name"]
        hours = loc["description"].replace("pm", "pm ").replace("day", "day ")
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        state = loc["address"]["addressRegion"]
        pcode = loc["address"]["postalCode"]
        phone = loc["telephone"]
        r = session.get(link, headers=headers, verify=False)
        try:
            longt = str(r.text.split('data-gmaps-lng="', 1)[1].split('"', 1)[0])
            lat = str(r.text.split('data-gmaps-lat="', 1)[1].split('"', 1)[0])
        except:
            continue
        if "COMING SOON" in hours:
            continue
        if "0.0" in lat:
            lat = longt = "<MISSING>"
        data.append(
            [
                "https://www.surcheros.com/",
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
