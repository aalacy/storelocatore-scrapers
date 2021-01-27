import csv
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
    locator_domain = "https://www.liquorandwineoutlets.com/"
    api_url = "https://www.liquorandwineoutlets.com/api/checkout/carts_storelist"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["value"]

    for j in js:
        adr1 = j.get("Address1") or ""
        adr2 = j.get("Address2") or ""

        if adr1 != adr2:
            street_address = f"{adr1} {adr2}".strip()
        else:
            street_address = adr1 or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("Postalcode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("Code") or "<MISSING>"
        page_url = "<MISSING>"
        location_name = j.get("Name")
        phone = j.get("PhoneNumber") or "<MISSING>"
        loc = j.get("Coords")
        latitude = loc.get("Latitude") or "<MISSING>"
        longitude = loc.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("ExtendedFields")
        for h in hours:
            day = h.get("DayOfTheWeek")
            start = h.get("OpenTime")
            close = h.get("CloseTime")
            _tmp.append(f"{day}: {start} - {close}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if hours_of_operation.count("TEMP - CLOSED") == 7:
            hours_of_operation = "Temporarily Closed"

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
