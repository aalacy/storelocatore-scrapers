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

    locator_domain = "https://www.triumph-motorcycles.ca/"
    api_url = (
        "https://www.triumph-motorcycles.ca/dealers/find-a-dealer?market=6&viewall=true"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="dealerListItem"]')

    for d in div:
        page_url = "".join(d.xpath('.//span[@class="openingTimes"]/a/@href')).replace(
            "triumph halifax", "triumph%20halifax"
        )
        location_name = (
            "".join(d.xpath('.//span[@class="dealerName"]/text()'))
            .replace("\n", "")
            .strip()
        )
        location_type = "<MISSING>"
        street_address = (
            "".join(d.xpath('.//div[@class="dealerAddress"]/span/text()[1]'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        cs = d.xpath('.//div[@class="dealerAddress"]/span/text()[2]')
        cs = list(filter(None, [a.strip() for a in cs]))
        cs = (
            "".join(cs)
            .replace("\r\n", "")
            .replace("Kelowna,", "Kelowna")
            .replace("Langley,", "Langley")
            .replace("Vancouver,", "Vancouver")
            .strip()
        )
        phone = (
            "".join(
                d.xpath(
                    './/strong[contains(text(), "Phone")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        state = "".join(cs.split(",")[0].split()[-1])
        postal = (
            "".join(d.xpath('.//div[@class="dealerAddress"]/span/text()[3]'))
            .replace("\r\n", "")
            .replace("B3Z", "B3Z ")
            .strip()
            or "<MISSING>"
        )
        country_code = "CA"
        city = " ".join(cs.split(",")[0].split()[:-1])
        if postal == "<MISSING>":
            postal = cs.split(",")[1].strip()
        store_number = "<MISSING>"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        latitude = "".join(
            tree.xpath('//img[@class="dealer-location__map-img"]/@data-map-lat')
        )
        longitude = "".join(
            tree.xpath('//img[@class="dealer-location__map-img"]/@data-map-lon')
        )
        hours_of_operation = tree.xpath(
            '//ul[@class="dealer-location__opening-times"]/li//text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation)

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
