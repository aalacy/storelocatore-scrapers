import csv

from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address


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
    locator_domain = "https://www.carphonewarehouse.com/"
    api_url = "https://www.carphonewarehouse.com/services/storedata?filter=&count=1000&lat=51.5073509&lng=-0.1277583"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json().values()

    for j in js:
        line = j.get("AddressLine") or ""
        postal = j.get("postcode") or ""
        if "ireland" in postal.lower() or "ireland" in line.lower():
            continue
        if "Currys" in line:
            line = ",".join(line.split(",")[1:])
            location_type = "Currys PC World"
        else:
            location_type = "<MISSING>"

        adr = parse_address(International_Parser(), line, postcode=postal)

        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )
        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        postal = adr.postcode or "<MISSING>"
        if len(street_address) < 10:
            street_address = line.split(",")[0].strip() or "<MISSING>"

        location_name = j.get("branch_name")
        if city == "<MISSING>":
            if location_name[0].isdigit() or location_name[0] == "(":
                city = " ".join(location_name.split()[1:])
            else:
                city = location_name
        country_code = "GB"
        store_number = j.get("branch_id") or "<MISSING>"
        phone = j.get("telephone") or "<MISSING>"
        if not phone[0].isdigit():
            phone = "<MISSING>"
        page_url = (
            f'https://www.carphonewarehouse.com/store-locator/{j.get("pageName")}.html'
        )
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"

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
            time = j.get(d)
            _tmp.append(f"{d.capitalize()}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
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
