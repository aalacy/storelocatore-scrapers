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

    locator_domain = "https://www.showbizcinemas.com"
    api_url = "https://www.showbizcinemas.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="More Info"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath('//div[@class="topAddressshowtimeInfo"]/div[2]/h5/text()')
        ).capitalize()
        location_type = "Cinema"
        street_address = "".join(
            tree.xpath('//div[@class="topAddressshowtimeInfo"]/div[2]/p/text()[1]')
        )
        ad = (
            "".join(
                tree.xpath('//div[@class="topAddressshowtimeInfo"]/div[2]/p/text()[2]')
            )
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()

        store_number = "<MISSING>"
        try:
            latitude = (
                "".join(tree.xpath("//div/@data-map"))
                .split('"lat":')[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath("//div/@data-map"))
                .split('"lng":')[1]
                .split(",")[0]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(
                tree.xpath('//div[@class="topAddressshowtimeInfo"]/div[1]/p[1]/text()')
            )
            .replace("Info:", "")
            .strip()
        )
        hours_of_operation = "<MISSING>"

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
