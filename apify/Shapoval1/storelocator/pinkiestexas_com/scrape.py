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
    locator_domain = "https://pinkiestexas.com"
    page_url = "https://pinkiestexas.com/locations/"

    session = SgRequests()
    r = session.get(page_url)

    tree = html.fromstring(r.text)

    divs = tree.xpath(
        "//div[contains(@class,'et_pb_column et_pb_column_1_3')]//div[@class='et_pb_text_inner']"
    )
    for d in divs:
        location_name = "".join(d.xpath(".//h2/strong/text()"))
        block = d.xpath(".//p[./a]")
        for b in block:

            street_address = "".join(
                b.xpath(
                    ".//preceding-sibling::p[1]/strong/text() | .//preceding-sibling::p[2]/strong/text()"
                )
            )
            ad = (
                " ".join(b.xpath(".//preceding-sibling::p[1]/text()[1]"))
                .replace("\n", "")
                .strip()
            )
            city = ad.split(",")[0]
            postal = ad.split(",")[1].strip().split()[-1]
            state = ad.split(",")[1].strip().split()[0]
            if state.find("Texas") != -1:
                state = "TX"
            country_code = "US"
            store_number = "<MISSING>"
            phone = (
                "".join(b.xpath(".//preceding-sibling::p[1]/text()[2]"))
                .replace("\n", "")
                .strip()
            )
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"
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
