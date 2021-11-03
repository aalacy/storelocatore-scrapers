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
    locator_domain = "https://www.princessauto.com"
    api_url = "https://mwprod-processing-princessauto.objectedge.com/api/location"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["items"]:

        location_name = j.get("name")
        street_address = f"{j.get('address1')} {j.get('address2') or ''} {j.get('address3') or ''}".replace(
            "second street", ""
        ).strip()
        city = j.get("city")
        state = j.get("state")
        country_code = j.get("country")
        postal = j.get("postalCode")
        store_number = j.get("locationId")
        page_url = f"https://www.princessauto.com/en/store?storeId={store_number}"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = j.get("type")
        hours = j.get("hours") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours = html.fromstring(hours)
            hours_of_operation = hours.xpath(
                '//h4[contains(text(), "Store Hours")]/following-sibling::ul[1]/li//text()'
            )
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation)
        phone = j.get("phoneNumber")

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
