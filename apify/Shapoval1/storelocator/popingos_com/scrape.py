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


def fetch_data():
    out = []

    locator_domain = "https://popingos.com"
    api_url = "https://popingos.com/js/mapData/oxbowConvertCsv.json?v20180711"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:

        page_url = f"https://{j.get('url')}"
        location_name = "".join(j.get("name"))

        location_type = "<MISSING>"
        street_address = f"{j.get('address')} {j.get('address 2')}".replace(
            "None", ""
        ).strip()
        phone = j.get("phone")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = j.get("country")
        city = j.get("city")
        try:
            store_number = page_url.split("-")[-1].replace("/", "").strip()
        except:
            store_number = "<MISSING>"
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[contains(text(), "Business")]/following-sibling::p//text()'
                )
            )
            .replace("\n", "")
            .strip()
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
