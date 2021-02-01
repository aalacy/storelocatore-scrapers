import csv
import usaddress
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
    locator_domain = "https://www.bottegaveneta.com"
    api_url = "https://www.bottegaveneta.com/experience/us/?yoox_storelocator_action=true&action=yoox_storelocator_get_all_stores"
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
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.bottegaveneta.com/experience/us/store-locator/",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        country_code = "<MISSING>"
        try:
            if country_code is not None:
                country_code = j.get("location").get("country").get("slug")
            else:
                continue
        except AttributeError:
            country_code = "<MISSING>"
        if country_code != "us" and country_code != "ca":
            continue
        line = "".join(j.get("wpcf-yoox-store-address")).replace("\n", "")
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = j.get("wpcf-city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        store_number = "<MISSING>"
        page_url = j.get("permalink")
        location_name = j.get("post_title")
        phone = "".join(j.get("wpcf-yoox-store-phone"))
        if phone.find("ext"):
            phone = phone.split("ext")[0].strip()
        if city == "Palm Desert":
            street_address = a.get("recipient")
        if city == "Carmel":
            street_address = (
                f"{a.get('address1')} {a.get('address2')} {a.get('city')}".replace(
                    "None", ""
                )
            )
        if city == "Vancouver":
            street_address = "".join(line.split(",")[:-2]).strip()
        if city == "Montreal":
            state = "".join(a.get("state")).split(",")[0]
            postal = line.split(",")[-1].strip()
        if city == "Toronto":
            state = "".join(a.get("state")).split(",")[0]
        if street_address.find("737") != -1:
            state = "".join(a.get("state")).split(",")[0]
            postal = line.split(",")[-1].strip()
            street_address = a.get("address1")
        if city == "North York":
            state = "".join(a.get("city")).split(",")[1].strip()
            postal = line.split(",")[-1].strip()
        if street_address.find("Airport") != -1:
            state = "".join(a.get("address2")).split()[0]
            postal = " ".join(line.split(",")[-2].split()[1:]).strip()
        if city == "Bellevue":
            state = "".join(a.get("address1")).split()[1]
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours = j.get("wpcf-yoox-store-hours").split("\n")
        hours = list(filter(None, [a.strip() for a in hours]))
        hours_of_operation = " : ".join(hours).replace("/", " ") or "<MISSING>"
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
