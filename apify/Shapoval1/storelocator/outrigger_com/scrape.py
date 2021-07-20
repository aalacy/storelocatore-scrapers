import csv
import usaddress
from lxml import html
from sgrequests import SgRequests
from concurrent import futures


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


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://www.outrigger.com/hotels-resorts", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath('//a[text()="View Hotel"]/@href')


def get_data(url):
    locator_domain = "https://www.outrigger.com"
    page_url = f"{locator_domain}{url}"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)
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
    info = tree.xpath(
        '//a[contains(@href, "email")]/preceding-sibling::text() | //span[contains(text(), "78-128 Ehukai")]/text() | //span[contains(text(), "P.O. Box 173")]/text() | //span[contains(text(), "Castaway Island, Fiji")]/text() | //a[contains(@href, "email")]/preceding-sibling::*/text()'
    )

    info = list(filter(None, [a.strip() for a in info]))
    ad = " ".join(info[:2])
    a = usaddress.tag(ad, tag_mapping=tag)[0]
    street_address = (
        f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
        or "<MISSING>"
    )
    if street_address == "69-250 Waikoloa Beach Drive":
        street_address = street_address + " " + "".join(info[2]).strip()
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
    if location_name.find("Ocean ViewOcean") != -1:
        location_name = location_name.split("Ocean ViewOcean")[0].strip()
    if location_name == "<MISSING>":
        location_name = "".join(tree.xpath("//h2/text()")) or "<MISSING>"
    if location_name.find("Save over") != -1:
        location_name = location_name.split("Save over")[0].strip()
    if location_name.find("Castaway Island, Fiji") != -1:
        city = location_name.split(",")[0].strip()
        state = location_name.split(",")[1].strip()
    if location_name.find("OUTRIGGER MAURITIUS BEACH RESORT") != -1:
        city = "".join(info[1]).split(",")[0].strip()
        state = "".join(info[1]).split(",")[1].strip()

    phone = (
        "".join(tree.xpath('//span/a[contains(@href, "tel")][1]/text()')).strip()
        or "<MISSING>"
    )
    if "".join(info).find("T:") != -1:
        try:
            phone = "".join(info).split("T:")[1].split("|")[0].strip() or "<MISSING>"
        except:
            phone = "<MISSING>"
    if "".join(info).find("Ph:") != -1:
        try:
            phone = (
                "".join(info).split("Ph:")[1].split("Fax:")[0].strip() or "<MISSING>"
            )
        except:
            phone = "<MISSING>"
    if phone.find("or") != -1:
        phone = phone.split("or")[0].strip()
    if phone.find("Reservations:") != -1:
        phone = phone.split("Reservations:")[0].strip()
    if "".join(info).find("Property Phone:") != -1:
        phone = "".join(info).split("Property Phone:")[1].split("Hawaii")[0].strip()
    phone = phone.replace("Toll-free", "").strip()

    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"
    cms = "".join(tree.xpath('//p[contains(text(), "Opening ")]/text()'))
    if cms:
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

    return row


def fetch_data():
    out = []
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
