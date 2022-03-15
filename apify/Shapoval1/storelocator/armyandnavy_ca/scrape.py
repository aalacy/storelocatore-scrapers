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

    locator_domain = "https://www.armyandnavy.ca"
    api_url = "https://www.armyandnavy.ca/pages/store-locations-1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h2[@style="text-align: left;"]')

    for d in div:
        page_url = "https://www.armyandnavy.ca/pages/store-locations-1"
        location_name = "".join(d.xpath(".//text()"))
        location_type = "<MISSING>"
        ad = (
            "".join(d.xpath('.//following-sibling::span[@class="rte"]/text()'))
            .replace("\n", "")
            .replace("New Westminster", "New_Westminster")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = "".join(
                d.xpath('.//following-sibling::p[./span[@class="rte"]]/span/text()')
            ).replace("New Westminster", "New_Westminster")

        street_address = " ".join(ad.split(",")[0].split()[:-1]).strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = " ".join(ad.split(",")[1].split()[1:]).strip()
        country_code = "CA"
        city = ad.split(".")[1].split(",")[0].split()[-1].replace("_", " ").strip()
        store_number = "<MISSING>"
        map_link = "".join(d.xpath(".//following::iframe[1]/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = "<MISSING>"
        hours_of_operation = (
            "".join(
                d.xpath(
                    ".//following-sibling::strong[1]//text() | .//following-sibling::p[1]/strong//text()"
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("CLOSED") != -1:
            hours_of_operation = "CLOSED".capitalize()

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
