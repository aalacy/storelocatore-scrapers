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
    locator_domain = "https://sostrenegrene.com/"
    api_url = (
        "https://sostrenegrene.com/umbraco/api/store/search?latitude=0&longitude=0"
    )
    headers = {"culture": "en-GB"}

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()["stores"]

    for j in js:
        j = j.get("store")

        line = j.get("address")
        print(line)

        adr = parse_address(International_Parser(), line)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )

        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        postal = adr.postcode or "<MISSING>"
        if postal == "<MISSING>":
            street_address = line.split(",")[0]
            postal = line.split(",")[1].replace(city, "").strip()

        country_code = "GB"
        store_number = j.get("id") or "<MISSING>"
        page_url = f'https://sostrenegrene.com{j.get("url")}'
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        loc = j.get("location")
        latitude = loc.get("latitude") or "<MISSING>"
        longitude = loc.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        hours = j.get("openingHours") or []
        if len(hours) > 7:
            hours = hours[:7]

        for h in hours:
            index = h.get("dayOfWeek")
            day = days[index]

            start = h.get("opens")
            if start:
                end = h.get("closes")
                _tmp.append(f"{day}: {start} - {end}")
            else:
                _tmp.append(f"{day}: Closed")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

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
