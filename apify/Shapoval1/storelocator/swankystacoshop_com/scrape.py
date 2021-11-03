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
    locator_domain = "https://www.swankystacoshop.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.post("https://www.swankystacoshop.com/locations", headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="templatecontent location"]')
    for d in div:

        page_url = "https://www.swankystacoshop.com/locations"
        street_address = "".join(d.xpath('.//a[contains(@href, "maps")]/text()[1]'))
        ad = (
            "".join(d.xpath('.//a[contains(@href, "maps")]/text()[2]'))
            .replace("\n", "")
            .replace("TN,", "TN")
            .strip()
        )
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        location_name = "".join(d.xpath(".//h3/text()"))
        country_code = "US"
        store_number = "<MISSING>"
        text = "".join(d.xpath('.//a[contains(@href, "google")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/p[./a[contains(text(), "Order Catering")]]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        cls = "".join(d.xpath('.//b[contains(text(), "closed ")]/text()'))
        if cls:
            hours_of_operation = "Closed"
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
