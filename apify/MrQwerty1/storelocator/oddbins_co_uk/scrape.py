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
    locator_domain = "https://www.oddbins.com/"
    page_url = "https://www.oddbins.com/pages/ourstores"
    api_url = "https://client.lifterlocator.com/maps/handlebarsGet/oddb.myshopify.com?storeName=oddb.myshopify.com&mapId=1497&plan=3"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["Record"]

    for j in js:
        line = j.get("address")
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

        if state == "<MISSING>" and postal == "<MISSING>":
            line = line.split(",")
            street_address = line[0].strip()
            city = line[1].strip()
            postal = line[2].strip()
            state = line[-1].strip()

        if state == "<MISSING>" and city == "London":
            state = "London"

        country_code = "GB"
        store_number = j.get("id") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("hours") or "<MISSING>"
        hours = hours.replace("\r", "").replace("\n", "").split("<br>")
        for h in hours[1:]:
            line = h.strip()
            if line[0].isalpha():
                _tmp.append(f"{line}: ")
            else:
                _tmp.append(f'{line.replace("to", "-")};')

        hours_of_operation = "".join(_tmp).strip() or "<MISSING>"
        if hours_of_operation.endswith(":") or hours_of_operation.endswith(";"):
            hours_of_operation = hours_of_operation[:-1]

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
