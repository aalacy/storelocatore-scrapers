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

    locator_domain = "https://weirsfurniture.com/"
    page_url = "https://weirsfurniture.com/locations-and-hours"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location"]')
    for d in div:

        location_name = "".join(d.xpath(".//h4/text()"))
        location_type = "<MISSING>"
        ad = d.xpath('.//p[@class="location-address"]/text()')
        ad = list(filter(None, [a.strip() for a in ad])) or "<MISSING>"
        street_address = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        city = "<MISSING>"
        if ad != "<MISSING>":
            street_address = "".join(ad[0]).strip()
            city = "".join(ad[1]).split(",")[0].strip()
            state = "".join(ad[1]).split(",")[1].split()[0].strip()
            postal = "".join(ad[1]).split(",")[1].split()[1].strip()
        store_number = "<MISSING>"
        country_code = "US"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = (
            "".join(d.xpath('.//p[@class="location-phone"]/text()[1]'))
            .replace("Phone:", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = d.xpath(
            './/p[@class="location-phone"]/following-sibling::p//text()'
        )
        hours_of_operation = (
            list(filter(None, [a.strip() for a in hours_of_operation])) or "<MISSING>"
        )
        if hours_of_operation != "<MISSING>":
            hours_of_operation = (
                " ".join(hours_of_operation[:-3])
                .replace("Store:", "")
                .replace("Hours:", "")
                .replace("  ", " ")
                .strip()
                + " "
                + "".join(hours_of_operation[-1]).strip()
            )
        tmpcls = "".join(
            d.xpath('.//span[contains(text(), "Closed for Redevelopment")]/text()')
        )
        if tmpcls:
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
