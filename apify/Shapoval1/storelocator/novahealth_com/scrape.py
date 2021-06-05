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

    locator_domain = "https://www.novahealth.com"
    api_url = "https://www.novahealth.com/wp-admin/admin-ajax.php?action=store_search&lat=44.05207&lng=-123.08675&max_results=10&search_radius=10&autoload=1"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.post(api_url, headers=headers)

    js = r.json()

    for j in js:

        page_url = j.get("url")
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = "".join(j.get("zip"))
        if postal.find("-") != -1:
            postal = postal.split("-")[0].strip()
        store_number = "<MISSING>"
        location_name = "Nova Health "
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        country_code = j.get("country")
        location_type = "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        hours_of_operation = tree.xpath(
            '//div[./div/h4[contains(text(), "Hours")]]/following-sibling::div//text() | //h2[contains(text(), "Hours")]/following-sibling::ul//text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = (
            " ".join(hours_of_operation).replace("Physical Therapy:", "").strip()
        )
        if (
            hours_of_operation.find("Primary Care: ") != -1
            and hours_of_operation.find("Urgent Care: ") != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("Urgent Care:")[1].split("Primary")[0].strip()
            )
        if hours_of_operation.find("Musculoskeletal") != -1:
            hours_of_operation = (
                hours_of_operation.split("Urgent Care:")[1]
                .split("Musculoskeletal")[0]
                .strip()
            )
        if hours_of_operation.find("Check back for updates!") != -1:
            hours_of_operation = "Coming Soon"
        if hours_of_operation.find("Physical & Hand Therapy") != -1:
            hours_of_operation = (
                hours_of_operation.split("Primary Care:")[1]
                .split("Physical & Hand Therapy")[0]
                .strip()
            )
        hours_of_operation = (
            hours_of_operation.replace("Urgent Care:", "")
            .replace("Primary Care:", "")
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
