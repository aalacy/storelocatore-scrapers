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

    locator_domain = "https://itan.com"

    api_url = "https://itan.com/wp-admin/admin-ajax.php?action=store_search&lat=32.79477&lng=-116.96253&max_results=150&search_radius=150&search=%20El%20Cajon&statistics%5Bcity%5D=El%20Cajon&statistics%5Bregion%5D=California&statistics%5Bcountry%5D=United%20States"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.post(api_url, headers=headers)
    js = r.json()

    for j in js:

        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        store_number = "<MISSING>"
        location_name = (
            "".join(j.get("store")).replace("&#8211;", "–").replace("&#8217;", "`")
        )
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        page_url = j.get("permalink")
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//rs-layer[contains(text(), "HOURS")]//following::rs-layer[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("HOLIDAY") != -1:
            hours_of_operation = hours_of_operation.split("HOLIDAY")[0].strip()

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
