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

    locator_domain = "https://www.angelikafilmcenter.com"
    api_url = "https://www.angelikafilmcenter.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="dropdown-slide-options"]/a')

    for d in div:

        page_url = locator_domain + "".join(d.xpath(".//@href"))
        location_name = "".join(d.xpath(".//text()"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_type = "Cinema"
        ad = (
            "".join(tree.xpath('//div[@class="footer-address clearfix"]/p/text()[3]'))
            .replace("\n", "")
            .strip()
        )
        street_address = (
            "".join(tree.xpath('//div[@class="footer-address clearfix"]/p/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        phone = "<MISSING>"
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        city = ad.split(",")[0].strip()
        country_code = "US"
        store_number = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
