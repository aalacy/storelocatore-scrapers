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

    locator_domain = "https://capstarbank.com"
    page_url = "https://capstarbank.com/Locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-block"]')
    for d in div:

        phone = (
            "".join(
                d.xpath('.//div[@class="city"]/following-sibling::div[1]/text()[1]')
            )
            .replace("P:", "")
            .strip()
        )
        ad = "".join(d.xpath('.//div[@class="city"]/text()'))
        if phone.find("or") != -1:
            phone = phone.split("or")[0].strip()
        location_type = "<MISSING>"
        street_address = "".join(d.xpath('.//div[@class="street"]/text()'))
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[0].strip()
        location_name = "".join(d.xpath(".//h2/text()"))
        store_number = "<MISSING>"
        text = "".join(d.xpath('.//a[@class="Speedbump"]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/div[./strong[text()="HOURS"]]/following-sibling::div[not(contains(text(), "Drive"))]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Drive") != -1:
            hours_of_operation = (
                "".join(
                    d.xpath(
                        './/div[./strong[text()="HOURS"]]/following-sibling::div/text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
                + " "
                + "".join(
                    d.xpath(
                        './/div[./strong[text()="HOURS"]]/following-sibling::div/text()[3]'
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
