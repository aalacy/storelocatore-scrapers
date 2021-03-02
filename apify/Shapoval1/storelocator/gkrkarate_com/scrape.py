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


def get_data():
    rows = []
    locator_domain = "https://www.fgkrkarate.com"
    session = SgRequests()
    data = {"action": "your-maps/map-pins"}
    r = session.post("https://www.gkrkarate.com/wp/wp-admin/admin-ajax.php", data=data)
    js = r.json()["items"]
    for j in js:
        location_name = "".join(j.get("name"))
        street_address = f"{j.get('streetNumber')} {j.get('streetName')}".replace(
            "None", ""
        ).strip()
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = j.get("country")
        if country_code != "United States" and country_code != "United Kingdom":
            continue
        store_number = "<MISSING>"
        page_url = j.get("link") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        phone = (
            "".join(tree.xpath('//span[@itemprop="telephone"]/a/text()')) or "<MISSING>"
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

        rows.append(row)
    return rows


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
