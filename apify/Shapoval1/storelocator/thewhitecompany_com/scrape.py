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

    locator_domain = "https://www.thewhitecompany.com"
    api_url = "https://www.thewhitecompany.com/uk/store-locator-endpoint/storesData"
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
    r = session.get(api_url, headers=headers)
    js = r.json()
    js = "".join(js).replace("false", "False").replace("true", "True")
    js = eval(js)
    for j in js["data"]["shops"]:

        a = j.get("address")
        page_url = f"https://www.thewhitecompany.com/uk/our-stores/{j.get('name')}"
        location_name = "".join(j.get("displayName")) or "<MISSING>"
        location_type = "<MISSING>"
        ad = f"{a.get('line1')} {a.get('line2')} {a.get('town')} {a.get('postalCode')}"

        street_address = f"{a.get('line1')} {a.get('line2')}".strip()
        state = "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("country").get("isocode") or "<MISSING>"
        city = a.get("town") or "<MISSING>"
        if country_code == "US":
            b = usaddress.tag(ad, tag_mapping=tag)[0]
            city = a.get("line2")
            state = b.get("state")
            postal = b.get("postal")
            street_address = f"{b.get('address1')} {b.get('address2')}".replace(
                "None", ""
            ).strip()
        store_number = "<MISSING>"
        latitude = j.get("geoPoint").get("latitude") or "<MISSING>"
        longitude = j.get("geoPoint").get("longitude") or "<MISSING>"
        if latitude == longitude:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = a.get("phone") or "<MISSING>"
        try:
            hours = j.get("openingHours").get("weekDayOpeningList") or "<MISSING>"
        except:
            hours = "<MISSING>"

        tmp = []
        if hours != "<MISSING>":
            for h in hours:
                day = h.get("weekDay")
                try:
                    opens = h.get("openingTime").get("formattedHour")
                except:
                    opens = "<MISSING>"
                try:
                    closes = h.get("closingTime").get("formattedHour")
                except:
                    closes = "<MISSING>"
                cls = h.get("closed")
                line = f"{day} {opens}-{closes}"
                if cls:
                    line = f"{day} Closed"
                tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"
        if hours_of_operation == "<MISSING>":
            try:
                hours = j.get("specialOpeningSchedule").get("weekDayOpeningList")
            except:
                hours = "<MISSING>"
            if hours != "<MISSING>":
                for h in hours:
                    day = h.get("weekDay")
                    try:
                        opens = h.get("openingTime").get("formattedHour")
                    except:
                        opens = "<MISSING>"
                    try:
                        closes = h.get("closingTime").get("formattedHour")
                    except:
                        closes = "<MISSING>"
                    cls = h.get("closed")
                    line = f"{day} {opens}-{closes}"
                    if cls:
                        line = f"{day} Closed"
                    tmp.append(line)

        hours_of_operation = "; ".join(tmp) or "<MISSING>"

        if location_name.find("PERMANENTLY CLOSED") != -1:
            hours_of_operation = "PERMANENTLY CLOSED"

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
