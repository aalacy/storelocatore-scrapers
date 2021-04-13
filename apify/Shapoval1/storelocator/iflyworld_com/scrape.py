import csv
from bs4 import BeautifulSoup
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

    locator_domain = "https://www.iflyworld.com"

    api_url = "https://www.iflyworld.com/find-a-location/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="wrap usa masonry"]/ul/li/a[@class="loc"]')
    for b in block:
        slug = "".join(b.xpath(".//@href"))
        page_url = f"https://www.iflyworld.com{slug}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath('//h2[@class="vig col"]/text()'))
        location_type = "<MISSING>"
        street_address = "".join(
            tree.xpath('//div[@class="sub-info contact"]/a[1]/text()[1]')
        ).strip()
        adr = "".join(
            tree.xpath('//div[@class="sub-info contact"]/a[1]/text()[2]')
        ).strip()
        phone = "".join(
            tree.xpath(
                '//div[@class="sub-info contact"]/a[contains(@href, "tel")]/text()'
            )
        ).strip()

        state = adr.split(",")[1].split()[0].strip() or "<MISSING>"
        postal = adr.split(",")[1].split()[-1].strip() or "<MISSING>"
        if postal.find("-") != -1:
            postal = postal.split("-")[0].strip()
        country_code = "US"
        city = adr.split(",")[0].strip() or "<MISSING>"
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h6[contains(text(), "HOURS")]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("coming soon") != -1:
            hours_of_operation = "Coming Soon"
        if hours_of_operation.find("will be closed") != -1:
            hours_of_operation = hours_of_operation.split(".")[1].strip()
        if hours_of_operation.find("will be closing") != -1:
            hours_of_operation = hours_of_operation.split(".")[1].strip()
        if hours_of_operation.find("April 1, 2021.") != -1:
            hours_of_operation = hours_of_operation.split("April 1, 2021.")[1].strip()
        if hours_of_operation.find("will be opening") != -1:
            hours_of_operation = "temporarily closed"
        if hours_of_operation.find("Currently taking limited") != -1:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("President's Day:") != -1:
            hours_of_operation = hours_of_operation.split("President's Day:")[0].strip()
        if hours_of_operation.find("Spring Break") != -1:
            hours_of_operation = hours_of_operation.split(")")[1].strip()

        ll = "".join(tree.xpath('//a[contains(@title, "Open in Google Maps")]/@href'))
        req = session.get(ll, headers=headers)
        maps = BeautifulSoup(req.text, "lxml")

        try:
            raw_gps = maps.find("meta", attrs={"itemprop": "image"})["content"]
            latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find("%")].strip()
            longitude = raw_gps[raw_gps.find("-") : raw_gps.find("&")].strip()
        except:
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
