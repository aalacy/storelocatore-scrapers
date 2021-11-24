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

    locator_domain = "https://www.rosesdiscountstores.com"
    apis = [
        "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=60.678584%2C-29.944849&southwest=20.148833%2C-121.351099",
        "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=61.106123%2C-53.323756&southwest=20.971747%2C-144.730006",
        "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=66.796259%2C-54.026881&southwest=32.556117%2C-145.433131",
        "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=67.445463%2C-29.856959&southwest=33.952516%2C-121.263209",
        "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=55.881503%2C-24.319849&southwest=11.361618%2C-115.726099",
        "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=69.87369%2C-35.130396&southwest=39.30884%2C-126.536646",
        "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=35.206678%2C-66.657125&southwest=19.068073%2C-96.276452",
        "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=47.396041%2C-92.970816&southwest=17.240655%2C-152.20947",
        "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=60.678584%2C-29.944849&southwest=20.148833%2C-121.351099",
        "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=36.795595%2C-85.664657&southwest=32.791309%2C-93.591418",
    ]
    s = set()
    for i in apis:
        session = SgRequests()
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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(i, headers=headers)
        js = r.json()

        for j in js["locations"]:
            page_url = "https://www.rosesdiscountstores.com/store-locator/"
            location_name = j.get("name") or "<MISSING>"
            location_type = "<MISSING>"

            ad = "".join(j.get("address"))
            a = usaddress.tag(ad, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            try:
                phone = j.get("contacts").get("con_wg5rd22k").get("text")
            except AttributeError:
                phone = "<MISSING>"
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
            country_code = "US"
            city = a.get("city") or "<MISSING>"
            store_number = "<MISSING>"
            latitude = j.get("lat") or "<MISSING>"
            longitude = j.get("lng") or "<MISSING>"
            try:
                hours = j.get("hours").get("hoursOfOperation")
            except AttributeError:
                hours = "<MISSING>"
            hours_of_operation = "<MISSING>"
            if hours != "<MISSING>":
                hours_of_operation = f"MON {hours.get('mon')} TUE {hours.get('tue')} WED {hours.get('wed')} THU {hours.get('thu')} FRI {hours.get('fri')} SAT {hours.get('sat')} SUN {hours.get('sun')}"
            ids = j.get("id")
            line = ids
            if line in s:
                continue
            s.add(line)
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
