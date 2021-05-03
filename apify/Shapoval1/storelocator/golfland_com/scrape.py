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
    locator_domain = "https://www.golfland.com"
    api_url = "https://www.golfland.com/wp-admin/admin-ajax.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    data = {
        "action": "csl_ajax_onload",
    }

    r = session.post(api_url, headers=headers, data=data)
    js = r.json()

    for j in js["response"]:

        location_name = j.get("name")
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        city = j.get("city")
        state = j.get("state")
        country_code = "US"
        postal = j.get("zip")
        store_number = "<MISSING>"
        page_url = "".join(j.get("url"))
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        phone = j.get("phone")
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)

        hours_of_operation = tree.xpath(
            '//h3[contains(text(), "Hours")]/following-sibling::div//text() | //i[@class="fas fa-clock"]/following-sibling::text() | //div[contains(text(), "Open")]/text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation).replace("Mini Golf Only", "")
        if hours_of_operation.find("Sunsplash") != -1:
            hours_of_operation = (
                hours_of_operation.split("Golfland")[1].split("Sunsplash")[0].strip()
            )
        if hours_of_operation.find("!") != -1:
            hours_of_operation = hours_of_operation.split("!")[1].strip()
        if hours_of_operation.find("Hours and Events") != -1:
            hours_of_operation = (
                hours_of_operation.split("Golfland")[1]
                .split("Hours and Events")[0]
                .strip()
            )
        if hours_of_operation.find("Golf sales") != -1:
            hours_of_operation = hours_of_operation.split("Golf sales")[0].strip()
        if hours_of_operation.find("Attraction") != -1:
            hours_of_operation = hours_of_operation.split("Attraction")[0].strip()

        if page_url.find("http://www.scandiafamilycenter.com") != -1:
            page_url = "https://www.golfland.com/locations/"
            hours_of_operation = "<INACCESSIBLE>"

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
