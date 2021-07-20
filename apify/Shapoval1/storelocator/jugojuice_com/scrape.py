import csv
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address


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

    locator_domain = "https://jugojuice.com/"
    api_url = "https://jugojuice.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en&t=1626731353763"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    tree = html.fromstring(r.content)
    div = tree.xpath("//locator/store/item")

    for d in div:

        page_url = (
            "".join(d.xpath(".//exturl/text()")) or "https://jugojuice.com/locations/"
        )
        ad = "".join(d.xpath(".//address/text()[1]")).replace("&#44;", ",")
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        if street_address == "15":
            street_address = ad.split(",")[0].strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        store_number = "<MISSING>"
        location_name = (
            "".join(d.xpath(".//location/text()"))
            .replace("&#39;", "`")
            .replace(" â", "")
        )
        latitude = "".join(d.xpath(".//latitude/text()"))
        longitude = "".join(d.xpath(".//longitude/text()"))
        country_code = "CA"
        location_type = "Jugo Juice"
        phone = "".join(d.xpath(".//telephone/text()"))
        hours_of_operation = (
            "".join(d.xpath(".//exturl/following-sibling::*[1]/text()")) or "<MISSING>"
        )
        if hours_of_operation != "<MISSING>":
            a = html.fromstring(hours_of_operation)
            hours_of_operation = a.xpath("//*//text()")
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = (
                " ".join(hours_of_operation)
                .replace("â", "")
                .replace("ââ", "")
                .replace(" <br> ", " ")
                .replace("<br>", "")
                .strip()
            )
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()

        if "Temporarily Closed" in location_name:
            location_type = "Temporarily Closed"
        if "temporarily closed" in location_name:
            location_type = "Temporarily Closed"

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
