from bs4 import BeautifulSoup
import csv
import usaddress
from sgrequests import SgRequests

session = SgRequests()


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

    url = "https://www.stopandgostores.com/locations"
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    stores = soup.find_all("div", {"role": "gridcell"})
    for store in stores:
        loc = store.find("h2").text
        ps = store.find_all("p")

        if len(ps) >= 3:
            if "phone" not in ps[1].text.lower():
                street = ps[0].text.strip()
                csz = ps[1].text.strip()
                phone = ps[2].text.lower().replace("phone", "").replace("x", "").strip()
            else:
                phone = ps[1].text.lower().replace("phone", "").replace("x", "").strip()
                ps = ps[0].text.split("\n")
                street = ps[0]
                csz = ps[1].strip()

        else:
            ps = ps[0].text.split("\n")
            street = ps[0]
            csz = ps[1].strip()
            phone = ps[2].lower().replace("phone", "").replace("x", "").strip()

        csz = usaddress.tag(csz.replace("\xa0", " "))[0]
        city = csz["PlaceName"]
        state = csz["StateName"]
        zip = csz["ZipCode"]

        if len(phone) < 10:
            phone = "<MISSING>"

        data.append(
            [
                "https://www.stopandgostores.com/",
                "https://www.stopandgostores.com/locations",
                loc,
                street.replace("\xa0", "").replace("S t", "St"),
                city,
                state,
                zip,
                "US",
                loc.split("#")[-1],
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
            ]
        )

    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
