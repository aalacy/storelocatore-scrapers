from bs4 import BeautifulSoup
import csv
import re
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
    pattern = re.compile(r"\s\s+")
    url = "https://www.judesbarbershop.com/location/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = (
        soup.find("ul", {"id": "nv-primary-navigation-main"})
        .findAll("ul", {"class": "sub-menu"})[1]
        .findAll("li", {"class": "menu-item"})
    )
    p = 0
    for div in divlist:
        link = div.find("a")["href"]
        r = session.get(link, headers=headers, verify=False)
        try:
            loclist = r.text.split('"@context": "https://schema.org",', 1)[1].split(
                "</script>", 1
            )[0]
        except:
            continue
        loclist = "{" + loclist
        loc = re.sub(pattern, "", loclist)
        loc = json.loads(loc)
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        state = loc["address"]["addressRegion"]
        pcode = loc["address"]["postalCode"]
        lat = loc["geo"]["latitude"]
        longt = loc["geo"]["longitude"]
        phone = loc["telephone"]
        title = loc["name"]
        hourlist = loc["openingHoursSpecification"]
        hours = ""
        for hour in hourlist:
            start = (int)(hour["opens"].split(":")[0])
            if start > 12:
                start = start - 12
            endstr = (int)(hour["closes"].split(":")[0])
            if endstr > 12:
                endstr = endstr - 12
            try:
                hours = (
                    hours
                    + hour["dayOfWeek"]
                    + " "
                    + str(start)
                    + ":"
                    + hour["opens"].split(":", 1)[1]
                    + " AM - "
                    + str(endstr)
                    + ":"
                    + hour["closes"].split(":", 1)[1]
                    + " PM  "
                )
            except:
                hours = (
                    hours
                    + ", ".join(hour["dayOfWeek"])
                    + "="
                    + str(start)
                    + ":"
                    + hour["opens"].split(":", 1)[1]
                    + " AM - "
                    + str(endstr)
                    + ":"
                    + hour["closes"].split(":", 1)[1]
                    + " PM  "
                )
                break
        data.append(
            [
                "https://www.judesbarbershop.com",
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
