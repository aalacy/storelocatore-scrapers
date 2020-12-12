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
    streetlist = []
    data = []
    pattern = re.compile(r"\s\s+")
    url = "https://www.flooringamerica.com/find-a-flooring-store/states"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.find("div", {"id": "stateList"}).select('a:contains(" Stores")')
    p = 0
    for div in statelist:
        statelink = "https://www.flooringamerica.com" + div["href"]
        r = session.get(statelink, headers=headers, verify=False)
        loclist = r.text.split('"@graph": ', 1)[1]
        loclist = re.sub(pattern, "", loclist).replace("\n", "").split("}]", 1)[0]
        loclist = loclist + "}]"
        loclist = json.loads(loclist)
        for loc in loclist:
            if loc["@type"] == "Corporation":
                continue
            title = loc["name"]
            link = loc["url"] + "about"
            phone = loc["telephone"]
            street = loc["address"]["streetAddress"]
            if street in streetlist:
                continue
            streetlist.append(street)
            state = loc["address"]["addressRegion"]
            pcode = loc["address"]["postalCode"]
            city = loc["address"]["addressLocality"]
            ccode = loc["address"]["addressCountry"]
            try:
                r = session.get(link, headers=headers, verify=False, timeout=10)
                hourlist = r.text.split("var data = ", 1)[1].split("}]", 1)[0]
                hourlist = json.loads(hourlist + "}]")
                hours = ""
                for hr in hourlist:
                    try:
                        hours = (
                            hours
                            + hr["DayOfWeek"]
                            + " "
                            + hr["OpenTime"].split(" ", 1)[1]
                            + " - "
                            + hr["CloseTime"].split(" ", 1)[1]
                            + " "
                        )
                    except:
                        hours = hours + hr["DayOfWeek"] + " Closed "
            except:
                hours = "<MISSING>"
            data.append(
                [
                    "https://www.flooringamerica.com",
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
                    "<MISSING>",
                    "<MISSING>",
                    hours,
                ]
            )

            p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
