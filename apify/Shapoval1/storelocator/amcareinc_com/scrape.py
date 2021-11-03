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

    locator_domain = "https://www.amcareinc.com/"
    api_url = "https://www.amcareinc.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="halves-buttons-pointer"]')

    for d in div:
        slug = "".join(d.xpath(".//@onclick")).split("'/")[1].split("'")[0]
        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        location_type = "<MISSING>"
        street_address = (
            "".join(tree.xpath('//div[@class="seventy-left"]/div[3]/text()[1]'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(tree.xpath('//div[@class="seventy-left"]/div[3]/text()[2]'))
            .replace("\n", "")
            .replace("Cincinnati", "Cincinnati,")
            .replace(",,", ",")
            .strip()
        )
        phone = (
            "".join(tree.xpath('//div[@class="seventy-left"]/div[3]/text()[3]'))
            .replace("\n", "")
            .replace("PH:", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "<MISSING>"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours = tree.xpath('//div[@class="seventy-left"]/div[2]//text()')
        hours_of_operation = " ".join(hours[:2]).replace("\r\n", "").strip()

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
