from bs4 import BeautifulSoup
import csv
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
    url = "https://www.muellerinc.com/o/services/mups/location/"
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()

    for loc in loclist:
        link = "https://www.muellerinc.com/o/services/mups/location/" + loc[
            "name"
        ].lower().strip().replace(" ", "-")
        if "coming-soon" in link:
            continue
        r = session.get(link, headers=headers, verify=False).json()
        store = str(r["locationId"])
        title = str(r["name"])
        lat = r["latitude"]
        longt = r["longitude"]
        phone = r["branchPhones"][0]["branchphonenumber"]
        phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
        street = r["addressline1"]
        if str(r["addressline2"]) == "":
            pass
        else:
            street = street + " " + r["addressline2"]
        city = r["city"]
        state = r["state"]
        pcode = r["zipcode"]
        hours = (
            BeautifulSoup(r["businesshourshtmltext"], "html.parser")
            .text.replace("\xa0", "")
            .replace("\n", " ")
            .strip()
        )
        link = "https://www.muellerinc.com/branchlocations/tx/" + loc[
            "name"
        ].lower().strip().replace(" ", "-")
        data.append(
            [
                "https://www.muellerinc.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
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
