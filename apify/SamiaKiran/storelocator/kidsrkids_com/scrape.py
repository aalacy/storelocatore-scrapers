import csv
import json
import html
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kidsrkids_com")

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
    final_data = []
    url = "https://kidsrkids.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split('"locations":')[1].split(',"states":', 1)[0]
    loclist = json.loads(loclist)
    street_list = []
    for loc in loclist:
        title = loc["title"]
        if "COMING SOON" in title:
            continue
        title = html.unescape(title)
        link = loc["link"]
        store = loc["ID"]
        if not store:
            store = "<MISSING>"
        lat = loc["lat"]
        longt = loc["lng"]
        ccode = loc["country"]
        phone = loc["phone"]
        if "TBD" in phone:
            phone = "<INACCESSIBLE>"
        hours = loc["hours"]
        address = loc["address"]
        address = address.replace(",", " ")
        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("Occupancy") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        if street in street_list:
            continue
        street_list.append(street)
        final_data.append(
            [
                "https://kidsrkids.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours,
            ]
        )
    return final_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
