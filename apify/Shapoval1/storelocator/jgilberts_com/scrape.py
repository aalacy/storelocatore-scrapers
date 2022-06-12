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

    locator_domain = "https://www.jgilberts.com"
    api_url = "https://www.jgilberts.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="title"]')

    for d in div:
        page_url = locator_domain + "".join(d.xpath(".//@href")) + "/contactus"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h2/text()"))
        location_type = "<MISSING>"
        street_address = (
            "".join(tree.xpath('//p[./a[contains(@href, "/maps/")]]/a/text()[1]'))
            .replace(",", "")
            .strip()
        )
        ad = (
            "".join(tree.xpath('//p[./a[contains(@href, "/maps/")]]/a/text()[2]'))
            .replace("\n", "")
            .strip()
        )

        phone = "".join(tree.xpath('//p[./a[contains(@href, "tel")]]/a/text()'))
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        text = "".join(tree.xpath('//a[contains(@href, "/maps/")]/@href'))
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
                tree.xpath(
                    '//p[./a[contains(@href, "tel")]]/following-sibling::p[position()<3]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Carry") != -1:
            hours_of_operation = hours_of_operation.split("Carry")[0].strip()

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
