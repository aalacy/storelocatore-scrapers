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

    locator_domain = "https://www.first-online.bank/"
    api_url = "https://www.first-online.bank/wp-admin/admin-ajax.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    data = {
        "store_locatore_search_input": "One First Financial Plaza  Terre Haute, United States",
        "store_locatore_search_radius": "500",
        "store_locator_category": "",
        "action": "make_search_request_custom_maps",
        "map_id": "4939",
        "lat": "39.466166",
        "lng": "-87.409383",
    }

    r = session.post(api_url, headers=headers, data=data)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[@class='store-locator-item ']")

    for d in div:

        location_name = "".join(d.xpath('.//div[@class="wpsl-name"]/a/text()'))

        location_type = "Branch"
        if location_name.find("ATM") != -1:
            location_type = "ATM"
        street_address = "".join(d.xpath('.//div[@class="wpsl-address"]/text()'))
        ad = "".join(d.xpath('.//div[@class="wpsl-city"]/text()'))
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[0].strip()
        page_url = "".join(d.xpath('.//div[@class="wpsl-name"]/a/@href'))
        store_number = page_url.split("p=")[1].strip()
        ll = "".join(d.xpath('.//a[@class="store-direction"]/@data-direction'))
        latitude = ll.split(",")[0]
        longitude = ll.split(",")[1]
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            tree.xpath(
                '//span[contains(text(), "Lobby Hours")]/following-sibling::span/text()'
            )
            or "<MISSING>"
        )
        if hours_of_operation != "<MISSING>":
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation)
        cls = "".join(tree.xpath('//span[contains(text(), "Lobby")]/text()'))
        phone = (
            "".join(
                tree.xpath(
                    '//span[contains(text(), "Phone")]/following-sibling::text()'
                )
            ).strip()
            or "<MISSING>"
        )
        if phone.find("-") == -1:
            phone = "<MISSING>"
        if hours_of_operation.find("Drive") != -1:
            hours_of_operation = hours_of_operation.split("Drive")[0].strip()
        if cls.find("Closed") != -1:
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
