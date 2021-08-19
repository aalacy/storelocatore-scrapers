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


def get_data():
    rows = []
    locator_domain = "http://uluke.com"
    api_url = "http://uluke.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMjSKUdIBiRRnlBZ4uhQDBaNjgQLJpcUl+blumak5KRCxWqVaABYfFuw"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Proxy-Authorization": "Basic YWNjZXNzX3Rva2VuOmc3NzExNnBzajZqbGZhaHM5dHJwMDdocm0ydTlxNGVzM3BhaGNrYm9oY2kzOGEzMWtpdQ==",
        "Connection": "keep-alive",
        "Referer": "http://uluke.com/locations",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
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
    cookies = {
        "__cfduid": "dcddb223eaa7e6b9226e1ca710b62fed61615411418",
        "_ga": "GA1.2.2080322278.1615411421",
        "_gid": "GA1.2.45641285.1615411421",
        "_gat": "1",
    }

    r = session.get(api_url, headers=headers, cookies=cookies)

    js = r.json()
    for j in js["markers"]:

        ad = "".join(j.get("address")).replace("\n", " ")

        a = usaddress.tag(ad, tag_mapping=tag)[0]

        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        state = a.get("state")
        if street_address.find("500") != -1:
            city = ad.split(",")[1].split(",")[0].strip()
            state = ad.split(",")[2].split(",")[0].strip()
        if state.find("USA") != -1:
            state = state.split(",")[0].strip()
        postal = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "<MISSING>"
        phone = "<MISSING>"
        page_url = "http://uluke.com/locations"
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours = j.get("description")
        hours = html.fromstring(hours)
        text = (
            " ".join(hours.xpath("//*/text()"))
            .replace("\n", " ")
            .replace("Luke Hours:   ", "")
            .strip()
        )
        if text.find("Luke") != -1:
            text = text.split("Luke")[0].strip()
        if text.find("**") != -1:
            text = text.split("**")[0].strip()
        if text.find(".") != -1:
            phone = text.split("  ")[-1].strip()
        if phone.find("pm") != -1:
            phone = phone.split("pm")[1].strip()

        if text.find("Car") != -1:
            text = " ".join(text.split("Car")[0].split())
        if text.find("2") != -1 and text.find("24") == -1:
            text = text.split("2")[0].strip()
        if text.find("7") != -1:
            text = text.split("7")[0].strip()
        if text.find("219") != -1:
            text = text.split("219")[0].strip()
        hours_of_operation = text

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

        rows.append(row)
    return rows


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
