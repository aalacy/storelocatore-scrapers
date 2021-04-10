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

    locator_domain = "https://www.bobmillsfurniture.com"
    api_url = "https://www.bobmillsfurniture.com/findastore.inc"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    div = tree.xpath('//div[@class="findastorerow"]')
    for d in div:

        location_type = "<MISSING>"
        store_number = "<MISSING>"

        ad = (
            "".join(d.xpath('.//div[@class="grid-33 tablet-grid-33"][1]/p/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        street_address = "".join(
            d.xpath('.//div[@class="grid-33 tablet-grid-33"][1]/p/text()[1]')
        )
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        if postal.find("-") != -1:
            postal = postal.split("-")[0].strip()
        country_code = "US"

        phone = "".join(
            d.xpath('.//div[@class="grid-33 tablet-grid-33"][1]/p/strong/text()')
        )

        slug = "".join(
            d.xpath('.//a[contains(text(), "view map & more information")]/@href')
        )
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(d.xpath(".//div/h2/a/text()"))
        if location_name.find("Distribution") != -1:
            page_url = "https://www.bobmillsfurniture.com/findastore.inc"

        text = "".join(
            d.xpath('.//a[contains(text(), "view map & more information")]/@href')
        )
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
            " ".join(d.xpath('.//div[@class="grid-33 tablet-grid-33"][3]//p//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.split(" Hours:")[1].replace("  ", " ").strip()
        )

        if page_url != "https://www.bobmillsfurniture.com/findastore.inc":
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            map_link = "".join(tree.xpath("//iframe/@src"))
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
