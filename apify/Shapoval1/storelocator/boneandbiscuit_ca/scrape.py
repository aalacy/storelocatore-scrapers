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
    locator_domain = "https://www.boneandbiscuit.ca"
    api_url = "https://www.boneandbiscuit.ca/location/"
    session = SgRequests()

    r = session.get(api_url)

    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col--listing-inner"]')

    for d in div:

        location_name = "".join(d.xpath(".//h5/a/text()")).replace("\n", "").strip()
        page_url = "".join(d.xpath('.//a[@class="btn btn-tertiary btn-sm"]/@href'))
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)

        ad = (
            " ".join(
                tree.xpath(
                    '//h4[contains(text(), "Address")]/following-sibling::a//text()'
                )
            )
            .replace("\n", "")
            .replace(",,", ",")
            .strip()
        )

        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        if ad != "" and ad.count(",") == 2:
            street_address = ad.split(",")[0].strip()

            city = ad.split(",")[1].strip()
            state = " ".join(ad.split(",")[2].split()[:-2]).strip()
            postal = " ".join(ad.split(",")[2].split()[-2:]).strip()

        if ad != "" and ad.count(",") == 3:

            street_address = ad.split(",")[0].strip() + " " + ad.split(",")[1].strip()
            city = ad.split(",")[2].strip()

            state = " ".join(ad.split(",")[3].split()[:-2]).strip()
            postal = " ".join(ad.split(",")[3].split()[-2:]).strip()

        if street_address.find("11939") != -1:
            state = " ".join(ad.split(",")[2].split()[:-2]).strip()
            postal = " ".join(ad.split(",")[2].split()[-2:]).strip()

        if street_address.find("500") != -1:
            state = "".join(ad.split(",")[2].split()[-2:]).strip()
            postal = "<MISSING>"

        country_code = "CA"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//ul[@class="listing-hours list-unstyled"]/li/span/text() | //ul[@class="listing-hours list-unstyled"]/li/span/span/text()'
                )
            )
            .replace("\n", "")
            .replace("\t", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("Holiday") != -1:
            hours_of_operation = hours_of_operation.split("Holiday")[0].strip()
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

        phone = (
            "".join(tree.xpath('//a[contains(@href, "tel")]/text()')).strip()
            or "<MISSING>"
        )

        if street_address == city == state == postal:
            hours_of_operation = "Coming Soon"

        cms = "".join(
            tree.xpath(
                '//h3[contains(text(), "Coming Soon")]/text() | //h3[contains(text(), "Coming")]/text()'
            )
        )
        if cms:
            hours_of_operation = "Coming Soon"

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
