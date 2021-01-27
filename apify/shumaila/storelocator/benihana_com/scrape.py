from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
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
    url = "https://www.benihana.com/wp-admin/admin-ajax.php?action=get_all_stores&lat=24.8608&lng=67.0104"
    loclist = session.post(url, headers=headers, verify=False).json()
    for loc in loclist:
        location = loclist[loc]
        store = location["ID"]
        title = location["na"]
        link = location["gu"]
        city = location["ct"]
        street = location["st"]
        state = location["rg"]
        pcode = location["zp"]
        ccode = location["co"]
        if len(street) < 2:
            street = city = pcode = "<MISSING>"
        if len(city) < 2:
            city = "<MISSING>"
        if len(state) < 2:
            state = "<MISSING>"
        if len(pcode) < 2:
            pcode = "<MISSING>"
        if "US" in ccode:
            pass
        else:
            continue
        try:
            phone = location["te"]
        except:
            phone = "<MISSING>"
        ltype = location["ca"]["0"]
        lat = location["lat"]
        longt = location["lng"]
        if "Event" in ltype:
            hours = "<MISSING>"
        else:
            r = session.get(link, headers=headers, verify=False).text
            soup = BeautifulSoup(r, "html.parser")

            if "Delivery" in ltype:

                hours = (
                    soup.find("div", {"class": "boxRight_1"})
                    .text.replace("\n", " ")
                    .strip()
                    .split("Hours ", 1)[1]
                )
            elif "Restaurant" in ltype:
                try:
                    hours = (
                        soup.find("div", {"class": "boxLeft_h"})
                        .select_one('li:contains("Dinner")')
                        .text.replace("\n", " ")
                        .strip()
                        .split("Dinner", 1)[1]
                    )
                except:
                    hours = (
                        soup.find("div", {"class": "boxLeft_h"})
                        .select_one('li:contains("Delivery")')
                        .text.replace("\n", " ")
                        .strip()
                        .split("Delivery", 1)[1]
                    )
        try:
            hours = hours.split(". OUTDOOR", 1)[0]
        except:
            pass
        data.append(
            [
                "https://www.benihana.com/",
                link,
                title.strip(),
                street.strip(),
                city.strip(),
                state.strip(),
                pcode.strip(),
                ccode,
                store.strip(),
                phone.strip(),
                ltype.strip().replace("&amp;", "&"),
                lat,
                longt,
                hours.strip().replace("&amp;", "&").replace("�", ""),
            ]
        )

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
