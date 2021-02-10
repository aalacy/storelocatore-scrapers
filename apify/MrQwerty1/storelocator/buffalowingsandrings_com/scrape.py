import csv
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


def get_phones():
    out = dict()
    session = SgRequests()
    r = session.get("https://www.buffalowingsandrings.com/locations")
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@class, 'cardgrid__card location__card')]")
    for d in divs:
        slug = "".join(d.xpath(".//a[@class='location__city']/@href")).split("/")[-1]
        line = d.xpath(".//address/text()")
        line = list(filter(None, [l.strip() for l in line]))
        phone = line[-1]
        out[slug] = phone

    return out


def fetch_data():
    out = []
    locator_domain = "https://www.buffalowingsandrings.com/"
    api_url = "https://www.buffalowingsandrings.com/locations.json"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()
    phones = get_phones()

    for j in js:
        street_address = j.get("address_1") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        slug = j.get("permalink")
        page_url = f"https://www.buffalowingsandrings.com/locations/{slug}"
        location_name = j.get("title")
        phone = phones[slug]
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            j.get("hours", "").replace("<br>", ";").replace("&amp;", "-") or "<MISSING>"
        )
        if hours_of_operation.find(";;") != -1:
            hours_of_operation = hours_of_operation.split(";;")[0].strip()

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
