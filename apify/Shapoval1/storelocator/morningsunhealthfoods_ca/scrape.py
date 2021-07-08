import csv
from sgscrape.sgpostal import International_Parser, parse_address
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

    locator_domain = "https://www.morningsunhealthfoods.ca"
    api_url = "https://www.morningsunhealthfoods.ca/static/js/12.17a993b1.chunk.js"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    jsblock = r.text.split("features:")[1].split("},p=t")[0].replace("!0", "0").strip()

    js = jsblock.split("{geometry:")
    for j in js:
        if j == "[":
            continue

        page_url = "https://www.morningsunhealthfoods.ca/locations"
        location_name = j.split('location:"')[1].split('"')[0].strip()
        ad = j.split('address:"')[1].split('"')[0].replace(", #313", " #313,").strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        city = a.city or "<MISSING>"
        store_number = "<MISSING>"
        phone = j.split('phone:"')[1].split('"')[0].strip()
        hours_of_operation = (
            j.split("hours:")[1]
            .split("}}")[0]
            .replace("{", "")
            .replace(":", " ")
            .replace('"', "")
            .replace(" 30", ":30")
            .strip()
        )
        if "permanentlyClosed" in j:
            hours_of_operation = "Permanently Closed"

        latitude = j.split("coordinates:[")[1].split(",")[0].strip()
        longitude = j.split("coordinates:[")[1].split(",")[1].split("]")[0].strip()
        location_type = j.split('category:"')[1].split('"')[0].strip()
        location_type = (
            location_type.replace("ahc", "Alive Health Centre")
            .replace("ms", "Morning Sun Health Foods")
            .replace("sp", "Supplements Plus")
        )

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
