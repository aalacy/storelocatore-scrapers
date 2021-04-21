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

    locator_domain = "https://www.sansotei.com/locations"
    page_url = "https://www.sansotei.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./p//a]")

    for d in div:

        location_name = "".join(d.xpath('.//span[@style="font-size:30px"]//text()'))

        location_type = "<MISSING>"
        street_address = "".join(
            d.xpath(
                './/a//span[@style="font-family:cormorantgaramond-light,cormorant garamond,serif"]//text()'
            )
        )

        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]/@href'))
            .replace("tel:", "")
            .strip()
        )
        adr = (
            " ".join(
                d.xpath(
                    './/a//span[@style="font-family:cormorantgaramond-light,cormorant garamond,serif"]/following::h3[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

        state = adr.split(",")[1].strip()
        postal = "<MISSING>"
        country_code = "Canada"
        city = adr.split(",")[0].strip()
        store_number = "<MISSING>"
        text = "".join(d.xpath('.//a[contains(@href, "/maps")]/@href'))
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
                    './/span[@style="font-family:oswald-extralight,oswald,sans-serif"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        tmpclz = "".join(
            d.xpath('.//span[contains(text(), "TEMPORARILY CLOSED")]/text()')
        )
        if tmpclz:
            hours_of_operation = "TEMPORARILY CLOSED"

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
