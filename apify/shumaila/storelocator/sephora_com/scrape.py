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
    p = 0
    datanow = []
    datanow.append("none")
    url = "https://www.sephora.com/happening/storelist"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("a", {"class": "css-121wlog"})
    for link in linklist:
        link = "https://www.sephora.com" + link["href"]
        r = session.get(link, headers=headers, verify=False)
        try:
            r = r.text.split('"stores":[')[1].split("}],")[0]
        except:
            continue
        r = r + "}"
        loc = json.loads(r)
        street = loc["address"]["address1"]
        ccode = loc["address"]["country"]
        state = loc["address"]["state"]
        city = loc["address"]["city"]
        pcode = loc["address"]["postalCode"]
        phone = loc["address"]["phone"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        store = loc["storeId"]
        ltype = "Store"
        link = "https://www.sephora.com" + loc["targetUrl"]
        title = loc["displayName"]
        hours = "<MISSING>"
        try:
            hours = (
                "Monday "
                + loc["storeHours"]["mondayHours"]
                + " Tuesday "
                + loc["storeHours"]["tuesdayHours"]
                + " Wednesday "
                + loc["storeHours"]["wednesdayHours"]
                + " Thursday "
                + loc["storeHours"]["thursdayHours"]
                + "Friday "
                + loc["storeHours"]["fridayHours"]
                + " Saturday "
                + loc["storeHours"]["saturdayHours"]
                + " Sunday "
                + loc["storeHours"]["sundayHours"]
            )
            hours = hours.replace("AM", " AM ").replace("PM", " PM ").replace("-", "- ")
        except:
            hours = loc["storeHours"]["closedDays"]
            if hours.find("Opening on") > -1:
                hours = "SOON"
            elif hours.find("closed") > -1:
                hours = "<MISSING>"
        if hours != "SOON":
            if len(phone) < 3:
                phone = "<MISSING>"
            if len(pcode) == 4:
                pcode = "0" + pcode
            if state == "NW":
                state = "WA"
            if store in datanow:
                pass
            else:
                datanow.append(store)
                data.append(
                    [
                        "https://www.sephora.com",
                        link,
                        title.rstrip().lstrip(),
                        street.replace("\r", "").replace("\n", " ").rstrip().lstrip(),
                        city.rstrip().lstrip(),
                        state.rstrip().lstrip(),
                        pcode.rstrip().lstrip(),
                        ccode.rstrip().lstrip(),
                        store,
                        phone.rstrip().lstrip(),
                        ltype,
                        lat,
                        longt,
                        hours.rstrip(),
                    ]
                )

                p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
