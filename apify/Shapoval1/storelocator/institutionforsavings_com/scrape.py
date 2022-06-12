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

    locator_domain = "https://www.institutionforsavings.com"
    api_url = "https://www.institutionforsavings.com/_/api/branches/42.8082034/-70.8707561/500"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["branches"]:

        location_name = j.get("name")
        location_type = "Branch"
        street_address = j.get("address")
        phone = j.get("phone")
        state = j.get("state")
        postal = j.get("zip")
        city = j.get("city")
        country_code = "US"
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("long")

        desc = j.get("description")
        desc = html.fromstring(desc)
        slug_url = "".join(desc.xpath("//div/a/@data-link-id"))
        page_url = f"{locator_domain}{slug_url}"
        if page_url.find("rowley") != -1:
            page_url = "https://www.institutionforsavings.com/locations/rowley"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            " ".join(
                tree.xpath('//td[text()="Office Hours"]/following-sibling::td//text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//td[text()="Lobby & Drive-up Hours"]/following-sibling::td//text()'
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
