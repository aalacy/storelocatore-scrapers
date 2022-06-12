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

    locator_domain = "https://sammyspizza.com/"
    api_url = "https://sammyspizza.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    tree = html.fromstring(r.text)
    div = "".join(
        tree.xpath('//script[contains(text(), "address_details_array.push")]/text()')
    )
    ll = "".join(div.split("state_locations['CA'].push("))

    div = html.fromstring(div)
    divs = div.xpath('//a[@class="color-3"]')
    for d in divs:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath(
                '//h2[@class="diy-h3 vb-text-color vb-heading-size vb-text-transform color-3"]/text()'
            )
        )

        ad = tree.xpath(
            '//h3[contains(text(), "Address")]/following-sibling::p//text()'
        )

        location_type = "<MISSING>"
        street_address = "".join(ad[3]).replace(" 	 ", " ")
        phone = "".join(ad[10])
        state = "".join(ad[5]).strip()
        postal = "".join(ad[7])
        country_code = "US"
        city = "".join(ad[4]).replace("\n", "").replace(",", "").strip()
        store_number = "<MISSING>"
        msslug = city + " " + state
        latitude = (
            ll.split(msslug)[1].split("]);")[0].split('", "')[1].split('",')[0].strip()
        )
        longitude = "-" + ll.split(msslug)[1].split('"-')[1].split('", "')[0]
        hours_of_operation = tree.xpath(
            '//h2[contains(text(), "Hours of Operation")]/following-sibling::ul/li//text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation).replace("PST", "")
        if hours_of_operation.count("Open 24h") == 7:
            hours_of_operation = "Open 24h"
        hours_of_operation = hours_of_operation.replace(",", "").strip()
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
