import csv
import usaddress
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ginoseast_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    r = session.get("https://www.ginoseast.com/locations", headers=headers)
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    soup = BeautifulSoup(r.text, "html.parser")
    for data in soup.find("div", {"id": "page-5db3337c9f175d60ba85158a"}).find_all(
        "h3"
    ):
        for link in data.find_all("a"):
            page_url = "https://www.ginoseast.com" + link["href"]
            r1 = session.get(page_url, headers=headers)
            soup1 = BeautifulSoup(r1.text, "html.parser")
            name = soup1.h1.text.strip()
            full = list(
                soup1.find_all("div", {"class": "col sqs-col-6 span-6"})[1]
                .find("div", {"class": "row sqs-row"})
                .stripped_strings
            )

            phone = "".join(full).split("Phone")[1].strip()
            if phone.find("Address") != -1:
                phone = phone.split("Address")[0].strip()

            if "coming soon" in phone.lower():
                continue

            adr = " ".join(full).split("Address")[1].strip()
            if adr.find("Phone") != -1:
                adr = adr.split("Phone")[0].strip()
            a = usaddress.tag(adr, tag_mapping=tag)[0]
            city = a.get("city") or "<MISSING>"
            state = a.get("state") or "<MISSING>"
            zipcode = a.get("postal") or "<MISSING>"

            if zipcode == "60665":
                zipcode = "60605"
            street = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            hours = (
                " ".join(full[1:-5])
                .replace("Now Open For Safe Indoor Dining Service", "")
                .strip()
            )
            if not hours:
                hours = "<MISSING>"
            store = []
            store.append("https://www.ginoseast.com")
            store.append(name)
            store.append(street)
            store.append(city)
            store.append(state)
            store.append(zipcode.replace("CA", "<MISSING>"))
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(
                hours.replace("Delivery & Curbside Pick-Up available ", "").replace(
                    " Delivery available after 5pm", ""
                )
            )
            store.append(page_url)

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
