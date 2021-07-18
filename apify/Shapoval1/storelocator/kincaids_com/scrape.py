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

    locator_domain = "https://www.kincaids.com/"
    api_url = "https://www.kincaids.com/location.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="btn btn-block btn-primary brdr"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(d.xpath(".//text()"))
        slug_loc_name = location_name.replace(" ", "").replace(".", "").strip().lower()
        latitude = (
            "".join(
                d.xpath('.//following::script[contains(text(), "var cities")]/text()')
            )
            .split(f"{slug_loc_name}")[1]
            .split(",")[1]
            .strip()
        )
        longitude = (
            "".join(
                d.xpath('.//following::script[contains(text(), "var cities")]/text()')
            )
            .split(f"{slug_loc_name}")[1]
            .split(",")[2]
            .split("]")[0]
            .strip()
        )
        location_type = "Restaurant"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            "".join(tree.xpath('//span[@class="cWhite"]/text()'))
            .replace("-", "")
            .strip()
        )
        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[1].strip()
        store_number = "<MISSING>"
        phone = "".join(tree.xpath('//span[@class="cWhite"]/span/text()')).strip()
        hours_of_operation = tree.xpath(
            '//div[@class="col-xs-12 col-sm-5 col-sm-offset-1 text-left-xs"]/p//text() | //div[@class="col-xs-12 col-sm-5 col-sm-offset-1 col-lg-4 col-lg-offset-2 text-left-xs"]/p//text() | //div[@class="col-xs-12 col-sm-5 col-sm-offset-1 col-lg-4 col-lg-offset-2 text-left-xs"]/text()'
        )
        if page_url.find("stpaul") != -1:
            hours_of_operation = tree.xpath(
                '//div[@class="col-md-12 col-sm-8 col-sm-offset-1 text-left-xs"]/text()'
            )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation).replace("Dinner:", "").strip()

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
