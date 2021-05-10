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


def get_phone(url):
    session = SgRequests()
    if url.startswith("www"):
        url = f"https://{url}"

    r = session.get(url)
    tree = html.fromstring(r.text)

    return (
        "".join(tree.xpath("//address/a[contains(@href, 'tel:')]/text()"))
        or "<MISSING>"
    )


def fetch_data():
    out = []
    locator_domain = "https://www.ihg.com/voco"
    api_url = "https://apis.ihg.com/hotels/v1/search/closedSearch/VXVX"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "ihg-language": "en-GB",
        "x-ihg-api-key": "se9ym5iAzaW8pxfBjkmgbuGjJcr3Pj6Y",
        "content-type": "application/json; charset=UTF-8",
        "Origin": "https://www.ihg.com",
        "Connection": "keep-alive",
        "Referer": "https://www.ihg.com/",
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()["hotelContent"]

    for j in js:
        p = j.get("profile")
        a = j.get("address")
        page_url = a.get("consumerFriendlyURL") or "<MISSING>"
        country_code = a.get("isoCountryCode") or "<MISSING>"
        if country_code not in {"GB", "US", "CA"}:
            continue

        a = a.get("translatedMainAddress")
        street_address = (
            f"{a.get('line1')} {a.get('line2') or ''}".strip() or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zipcode") or "<MISSING>"

        store_number = j.get("hotelCode") or "<MISSING>"
        location_name = p.get("name")
        phone = get_phone(page_url)
        loc = p.get("latLong")
        latitude = loc.get("latitude") or "<MISSING>"
        longitude = loc.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
