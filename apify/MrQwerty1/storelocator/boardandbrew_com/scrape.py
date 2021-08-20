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


def get_hours(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    hours = tree.xpath(
        "//h4[@class='elementor-heading-title elementor-size-default']/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hoo = ";".join(hours) or "<MISSING>"
    hoo = (
        hoo.replace(" | ", ": ")
        .replace("OPEN DAILY;", "OPEN DAILY ")
        .replace("HOURS: ", "")
    )
    if "Special" in hoo:
        hoo = "<MISSING>"

    return hoo


def fetch_data():
    out = []
    locator_domain = "https://boardandbrew.com/"
    api_url = "https://boardandbrew.com/wp-admin/admin-ajax.php?action=store_search&autoload=1"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        street_address = f"{j.get('address')} {j.get('address2') or ''}".strip()
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("store")
        phone = j.get("phone") or "<MISSING>"
        if "walk" in phone.lower():
            phone = "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        if page_url != "<MISSING>":
            hours_of_operation = get_hours(page_url)
        else:
            hours_of_operation = "<MISSING>"

        if "<" in location_name:
            if "coming" in location_name.lower():
                hours_of_operation = "Coming Soon"

            location_name = location_name.split("<")[0].strip()

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
