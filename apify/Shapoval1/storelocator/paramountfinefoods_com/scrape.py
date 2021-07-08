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

    locator_domain = "https://paramountfinefoods.com/"
    api_url = "https://paramountfinefoods.com/"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="marker text-center"]')
    for d in div:
        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-lng"))
        page_url = "".join(d.xpath('.//a[contains(@href, "menu-locations")]/@href'))
        if page_url.find("pakistan") != -1:
            continue

        location_name = " ".join(d.xpath('.//p[contains(@class, "brandFont2")]/text()'))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_type = "<MISSING>"
        street_address = "".join(
            tree.xpath('//div[contains(@class, "location")]//p[@class="m-0"]/text()[1]')
        ).replace(",", "")
        if street_address.find("CF Rideau Ctr-50") != -1:
            street_address = street_address.split(".")[0]
        adr = (
            "".join(
                tree.xpath(
                    '//div[contains(@class, "location")]//p[@class="m-0"]/text()[2]'
                )
            )
            .replace("\n", "")
            .replace("Quebec", "Quebec Quebec")
            .replace("Brampton,", "Brampton")
            .strip()
        )
        phone = (
            "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone.find("416-903-3776647- 588 -3776") != -1:
            phone = phone.replace("416-903-3776647- 588 -3776", "416-903-3776").strip()
        if page_url.find("university-of-ottawa/#tab=location") != -1:
            adr = " ".join(street_address.split()[3:]).replace("Ontario", "Ontario,")
            street_address = " ".join(street_address.split()[:3])

        if page_url.find("kensington-london") != -1:
            adr = " ".join(street_address.split()[3:]).replace("United Kingdom", "UK,")
            street_address = " ".join(street_address.split()[:3])

        state = adr.split()[1].replace(",", "")
        postal = adr.split(",")[1].strip()
        country_code = "Canada"
        if location_name.find("UK") != -1:
            country_code = "UK"
        if state == "UK":
            state = "<MISSING>"
            country_code = "UK"
        city = adr.split()[0].strip()
        store_number = "<MISSING>"

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[contains(text(), "Opening")]/following-sibling::p//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = hours_of_operation.replace(
            ": 11:00am-9:00pm Friday-Saturday: 11:00am - 9:00pm",
            "Sunday-Thursday: 11:00am-9:00pm Friday-Saturday: 11:00am - 9:00pm",
        )
        if location_name.find("Temporarily Closed") != -1:
            hours_of_operation = "Temporarily Closed"
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
