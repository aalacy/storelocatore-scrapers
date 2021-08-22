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

    locator_domain = "https://www.pitfirepizza.com"
    api_url = "https://www.pitfirepizza.com/locals"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[contains(@class, 'col2')]/div[./h2]")
    asd = tree.xpath('//div[@id="submenu"]/div/ul/li/a/@data-option-value')
    i = 0
    for d in div:

        location_name = (
            "".join(d.xpath(".//h2//text()"))
            .replace("\n", "")
            .replace("  |  ", " | ")
            .strip()
        )
        page_url = "https://www.pitfirepizza.com/" + "".join(asd[i]).replace(".", "")
        i += 1
        if location_name.find("MAR VISTA") != -1:
            page_url = "https://www.pitfirepizza.com/mar-vista"
        if location_name.find("NORTH HOLLYWOOD") != -1:
            page_url = "https://www.pitfirepizza.com/north-hollywood"
        location_type = "<MISSING>"
        street_address = (
            "".join(
                d.xpath(
                    './/span[contains(text(), "LOCATION:")]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                d.xpath(
                    './/span[contains(text(), "LOCATION:")]/following-sibling::text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if street_address.find("966") != -1:
            street_address = (
                street_address
                + " "
                + "".join(
                    d.xpath(
                        './/span[contains(text(), "LOCATION:")]/following-sibling::text()[2]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            ad = (
                "".join(
                    d.xpath(
                        './/span[contains(text(), "LOCATION:")]/following-sibling::text()[3]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        phone = (
            "".join(
                d.xpath(
                    './/span[contains(text(), "PHONE:")]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        state = " ".join(ad.split()[-2:]).split()[0].strip()
        postal = " ".join(ad.split()[-2:]).split()[1].strip()
        country_code = "US"
        city = " ".join(ad.split()[:-2])
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/span[contains(text(), "HOURS:")]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
            + " "
            + " ".join(
                d.xpath(
                    './/span[contains(text(), "HOURS:")]/following-sibling::text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
            + " "
            + " ".join(
                d.xpath(
                    './/span[contains(text(), "HOURS:")]/following-sibling::text()[3]'
                )
            )
            .replace("\n", "")
            .strip()
            + " "
            + " ".join(
                d.xpath(
                    './/span[contains(text(), "HOURS:")]/following-sibling::text()[4]'
                )
            )
            .replace("\n", "")
            .strip()
            + " "
            + " ".join(
                d.xpath(
                    './/span[contains(text(), "HOURS:")]/following-sibling::text()[5]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()
        session = SgRequests()
        r = session.get("https://pitfirepizza.olo.com/locations/ca", headers=headers)
        tree = html.fromstring(r.text)
        latitude = (
            "".join(
                tree.xpath(
                    f'//div[contains(text(), "{phone}")]/following-sibling::span[@class="geo"]/span[@class="latitude"]/span/@title'
                )
            )
            or "<MISSING>"
        )
        longitude = (
            "".join(
                tree.xpath(
                    f'//div[contains(text(), "{phone}")]/following-sibling::span[@class="geo"]/span[@class="longitude"]/span/@title'
                )
            )
            or "<MISSING>"
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
