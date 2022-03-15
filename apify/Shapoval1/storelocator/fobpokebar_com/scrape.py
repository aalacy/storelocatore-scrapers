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

    locator_domain = "https://fobpokebar.com/"
    page_url = "https://fobpokebar.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h4]")
    for d in div:

        location_name = "".join(d.xpath(".//h4/text()"))
        location_type = "<MISSING>"
        street_address = "".join(d.xpath(".//p[1]/text()[1]")).replace(",", "").strip()
        ad = "".join(d.xpath(".//p[1]/text()[2]")).replace("\n", "").strip()
        state = ad.split()[1].strip()
        postal = ad.split()[2].strip()
        country_code = "US"
        city = ad.split()[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = (
            "".join(d.xpath('.//p[contains(text(), "Phone#")]/text()'))
            .replace("Phone#", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath('.//p[contains(text(), "Hours:")]/text()'))
            .replace("Hours:", "")
            .replace("\n", "")
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
