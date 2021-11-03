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

    locator_domain = "https://www.campisis.us"
    api_url = "https://www.campisis.us/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-xs-12 col-sm-6 col-md-4 zeropadding "]')
    for d in div:
        page_url = "".join(
            d.xpath('.//a[@class="sublocation-link elegant coverbk"]/@href')
        )
        location_name = "".join(d.xpath('.//h3[@class="elegant"]/text()'))
        location_type = "Restaurant"
        street_address = (
            "".join(d.xpath(".//ol/li[2]/text()[1]")).replace("\n", "").strip()
        )
        ad = "".join(d.xpath(".//ol/li[2]/text()[2]")).replace("\n", "").strip()
        phone = "".join(d.xpath(".//ol/li[4]//a/text()")).replace("\n", "").strip()
        city = ad.split(",")[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        state = ad.split(",")[1].split()[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            "".join(d.xpath(".//ol/li[last()]/text()"))
            .replace("\n", "")
            .replace("Daily", "")
            .strip()
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
