import csv

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address, International_Parser


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
    locator_domain = "https://semichem.co.uk/"
    page_url = "https://semichem.co.uk/store-finder/"
    api_url = "https://semichem.co.uk/store-finder/stores/"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        adr1 = j.get("address_line_1") or ""
        adr2 = j.get("address_line_2") or ""
        adr3 = j.get("address_line_3") or ""
        if adr3:
            line = f"{adr1},{adr2},{adr3}".strip()
        else:
            line = f"{adr1},{adr2}".strip()
        postal = j.get("postcode") or "<MISSING>"

        adr = parse_address(International_Parser(), line, postcode=postal)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )

        if len(street_address) <= 5:
            street_address = adr1.strip()

        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        postal = adr.postcode or "<MISSING>"
        country_code = "GB"
        store_number = j.get("store_id") or "<MISSING>"
        location_name = j.get("title") or "<MISSING>"
        phone = j.get("telephone_number") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for d in days:
            part = d[:3]
            start = j.get(f"ot_{part}_open")
            close = j.get(f"ot_{part}_close")
            if not close:
                _tmp.append(f"{d.capitalize()}: Closed")
            else:
                _tmp.append(
                    f"{d.capitalize()}: {start[:2]}:{start[2:]} - {close[:2]}:{close[2:]}"
                )

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address.strip(),
            city.strip(),
            state.strip(),
            postal.strip(),
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
