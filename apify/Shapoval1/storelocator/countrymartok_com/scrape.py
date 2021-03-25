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


def get_data():
    rows = []
    locator_domain = "https://www.countrymartok.com"
    api_url = "https://www.countrymartok.com/StoreLocator/State/?State=OK"
    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//td[@align="right"]')
    for d in div:
        slug = "".join(
            d.xpath('.//a[contains(@title, "View information about store")]/@href')
        )
        if slug == "":
            continue
        slug = slug.split("?")[1].split("&")[0]
        page_url = (
            f"https://www.countrymartok.com/StoreLocator/Store?{slug}&M=&From=&S="
        )
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        ad = (
            " ".join(tree.xpath('//p[@class="Address"]/text()'))
            .replace("\n", "")
            .replace("\t", "")
            .strip()
        )
        street_address = " ".join(ad.split(",")[0].split()[:-1])
        city = "".join(ad.split(",")[0].split()[-1]).strip()
        state = "".join(ad.split(",")[1].split()[0]).strip()
        postal = "".join(ad.split(",")[1].split()[-1]).strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "Country Mart"
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
        ll = (
            "".join(tree.xpath('//script[contains(text(), "initializeMap")]/text()'))
            .split("initializeMap(")[1]
            .split(");")[0]
            .replace('"', "")
        )
        latitude = ll.split(",")[0]
        longitude = ll.split(",")[1]
        location_type = "<MISSING>"
        hours_of_operation = "".join(
            tree.xpath(
                '//dt[contains(text(), "Hours of")]/following-sibling::dd/text()'
            )
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

        rows.append(row)
    return rows


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
