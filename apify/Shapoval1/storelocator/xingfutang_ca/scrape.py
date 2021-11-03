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

    locator_domain = "https://xingfutang.ca"
    page_url = "https://xingfutang.ca/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./div/div/div/h4[contains(text(), "XING FU TANG")]]')

    for d in div:

        location_name = "".join(
            d.xpath('.//div[@class="et_pb_text_inner"]/h4[1]/text()')
        )
        adr = (
            "".join(d.xpath('.//div[@class="et_pb_text_inner"]/h4[2]/text()'))
            .replace(", S.E.", " S.E.")
            .replace("BC,", "BC")
            .replace("AB,", "AB")
            .strip()
        )
        if adr.find("3432") != -1:
            adr = adr.replace("Street", "Street,")
        location_type = "<MISSING>"
        street_address = adr.split(",")[0].strip()
        phone = "".join(
            d.xpath('.//strong[contains(text(), "Phone")]/following-sibling::a//text()')
        ).strip()
        state = adr.split(",")[2].split()[0].strip()
        postal = " ".join(adr.split(",")[2].split()[1:]).strip()
        country_code = "Canada"
        city = adr.split(",")[1].strip()
        store_number = "<MISSING>"
        map_link = "".join(d.xpath(".//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/strong[contains(text(), "Hours")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("until") != -1:
            hours_of_operation = hours_of_operation.split("until")[0].strip()

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
