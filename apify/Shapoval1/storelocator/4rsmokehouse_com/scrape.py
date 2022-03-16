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

    locator_domain = "https://www.4rsmokehouse.com"

    api_url = "https://www.4rsmokehouse.com/wp-admin/admin-ajax.php?action=store_search&lat=28.54167&lng=-81.37569&max_results=25&search_radius=500"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "".join(j.get("url"))

        location_name = "".join(j.get("store")).strip()
        location_type = "<MISSING>"
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        latitude = j.get("lat")
        longitude = j.get("lng")
        country_code = j.get("country")
        state = j.get("state")
        postal = j.get("zip")
        city = j.get("city")
        store_number = "<MISSING>"
        hours = j.get("hours")
        hours = html.fromstring(hours)
        hours_of_operation = (
            " ".join(hours.xpath("//*/text()")).replace("\n", "").strip()
        )
        session = SgRequests()
        if (
            page_url.find("https://www.4rsmokehouse.com/locations/atlanta-coming-2017/")
            != -1
            or page_url.find("https://www.4rsmokehouse.com/locations/downtown-orlando/")
            != -1
        ):
            page_url = "https://www.4rsmokehouse.com/locations/"

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = (
            "".join(
                tree.xpath(
                    '//h2[contains(text(), "Contact")]/following-sibling::p/text()[2]'
                )
            )
            .replace("\n", "")
            .replace("(", "")
            .replace(")", "")
            .strip()
            or "<MISSING>"
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
