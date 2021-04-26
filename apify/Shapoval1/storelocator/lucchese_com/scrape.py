import csv
import usaddress
from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []
    locator_domain = "https://www.lucchese.com"
    page_url = "https://www.lucchese.com/stores"
    session = SgRequests()

    r = session.get(page_url)
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
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="card h-100"]')
    for b in block:
        ad = b.xpath('.//p[@class="card-text"]/text()')
        ad = list(filter(None, [a.strip() for a in ad]))
        ad = " ".join(ad)
        if ad.find("STOCKYARDS") != -1:
            ad = ad.split("STOCKYARDS")[1].strip()
        if ad.find("NOW OPEN") != -1:
            ad = ad.split("NOW OPEN")[1].strip()
        if ad.find("Open to trade by appointment") != -1:
            ad = ad.split("Open to trade by appointment")[1].strip()
        if ad.find("only") != -1:
            ad = ad.split("only")[1].strip()
        a = usaddress.tag(ad, tag_mapping=tag)[0]

        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        state = a.get("state")
        if street_address.find("57 Old") != -1:
            street_address = " ".join(ad.split(",")[0].split()[:-2])
            city = " ".join(ad.split(",")[0].split()[-2:])

        country_code = "US"
        store_number = "<MISSING>"
        postal = a.get("postal")
        location_name = (
            "".join(b.xpath('.//h5[@class="card-title"]/text()'))
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(b.xpath('.//li[@class="list-group-item store-card-phone"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone.find("EXT") != -1:
            phone = phone.split("EXT")[0].strip()
        text = "".join(b.xpath(".//a[contains(text(), 'Experience our store')]/@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if street_address.find("11751") != -1:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "Store"
        if (
            location_name.find("Outlet") != -1
            and location_name.find("Outlet Pop-Up") == -1
        ):
            location_type = "Outlet"
        if (
            location_name.find("Showroom") != -1
            and location_name.find("Showroom & Retail") == -1
        ):
            location_type = "Showroom"
        hours_of_operation = b.xpath(
            './/li[@class="list-group-item store-card-hours"]//text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = ";".join(hours_of_operation) or "<MISSING>"
        if hours_of_operation.find("NEW YEARS DAY") != -1:
            hours_of_operation = " ".join(hours_of_operation.split(";")[1:])
        if hours_of_operation.find("NOW OPEN:;") != -1:
            hours_of_operation = hours_of_operation.replace("NOW OPEN:;", "").strip()
        if hours_of_operation.find("Custom") != -1:
            hours_of_operation = hours_of_operation.split("Custom")[0].strip()
        if hours_of_operation.find("NEW YEARS DAY") != -1:
            hours_of_operation = hours_of_operation.split("12 pm–5 pm")[1].strip()
        if hours_of_operation.find("OPEN DURING ALLEN") != -1:
            hours_of_operation = hours_of_operation.split("HOURS;")[1].strip()
        if location_name.find("COMING SOON") != -1:
            hours_of_operation = "Coming Soon"

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
