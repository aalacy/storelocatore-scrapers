import csv
from bs4 import BeautifulSoup
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
    url = "https://www.tobycarvery.co.uk/restaurants?search=#"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select("a[href*=restaurants]")
    streetlist = []
    p = 0
    for div in divlist:
        link = div["href"]
        if link in streetlist:
            continue
        streetlist.append(link)
        r = session.get(link, headers=headers, verify=False)
        loc = r.text.split('<script type="application/ld+json">', 1)[1].split(
            "</script", 1
        )[0]
        loc = loc.replace("\n", "").strip()
        loc = json.loads(loc)
        title = loc["name"]
        phone = loc["telephone"]
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        try:
            state = loc["address"]["addressRegion"]
        except:
            state = "<MISSING>"
        pcode = loc["address"]["postalCode"]
        ccode = loc["address"]["addressCountry"]
        lat = loc["geo"]["latitude"]
        longt = loc["geo"]["longitude"]
        hourslist = json.loads(str(loc["openingHoursSpecification"]).replace("'", '"'))
        hours = ""
        for hr in hourslist:
            opens = hr["opens"]
            closes = hr["closes"]
            if opens.split(":")[0] == "00":
                time = "Closed"
            else:
                time = opens + "-" + closes
            hours = hours + hr["dayOfWeek"][0] + " " + time + " "
        data.append(
            [
                "https://www.tobycarvery.co.uk/",
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
                longt,
                lat,
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
