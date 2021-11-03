import csv
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
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

    locator_domain = "https://premieremoisson.com/"
    api_url = "https://premieremoisson.com/en/branches"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="branch"]')
    for d in div:
        ad = " ".join(d.xpath('.//p[@class="address"]/text()'))

        a = parse_address(International_Parser(), ad)

        location_name = "".join(d.xpath('.//p[@class="main-text"]/text()'))
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        if ad.find("5199") != -1:
            street_address = " ".join(ad.split(",")[0].split()[:-1]).strip()
            state = ad.split(",")[1].split()[0]
            postal = " ".join(ad.split(",")[1].split()[1:])
            city = ad.split(",")[0].split()[-1]
        if street_address.find("860") != -1:
            state = state.split()[0].strip()
        page_url = "".join(d.xpath(".//@href"))
        openclose = "".join(d.xpath('.//div[@class="caption"]/span[1]/text()'))

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_type = "<MISSING>"
        phone = "".join(tree.xpath('//a[@class="phone-link"]/text()'))
        country_code = "CA"
        store_number = "<MISSING>"
        ll = (
            "".join(tree.xpath('//script[contains(text(), "MAP CONTACT")]/text()'))
            .split("center: {")[1]
            .split("}")[0]
            .replace("lat:", "")
            .replace("lng:", "")
            .strip()
        )
        latitude = ll.split(",")[0].strip()
        longitude = ll.split(",")[1].strip()
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="hours"]/div/p/text()'))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"
        if openclose == "Closed":
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
