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
    locator_domain = "https://www.unibank.com"
    api_url = "https://www.unibank.com/_/api/branches/42.1116645/-71.6618658/50"

    session = SgRequests()
    r = session.get(api_url)

    js = r.json()
    for j in js["branches"]:

        street_address = j.get("address")
        city = j.get("city")
        postal = j.get("zip")
        state = j.get("state")
        phone = j.get("phone")
        country_code = "US"
        store_number = "<MISSING>"
        location_name = j.get("name")
        latitude = j.get("lat")
        longitude = j.get("long")
        location_type = "<MISSING>"

        description = j.get("description")
        desc = html.fromstring(description)
        hours_of_operation = (
            " ".join(desc.xpath('//div[contains(text(), "day")]//text()'))
            or "<MISSING>"
        )
        page_url = (
            "".join(desc.xpath("//a/@href"))
            or "https://www.unibank.com/locations#locationTable"
        )
        if street_address.find("1189") != -1:
            session = SgRequests()
            sr = session.get(page_url)
            trees = html.fromstring(sr.text)
            hours_of_operation = (
                " ".join(trees.xpath('//p[@class="open-hour"]/span/text()'))
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
