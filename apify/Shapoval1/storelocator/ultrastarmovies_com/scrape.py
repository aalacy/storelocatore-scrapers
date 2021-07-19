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

    locator_domain = "https://ultrastarmovies.com/#"
    api_url = "https://ultrastarmovies.com/#"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h4[text()="Our Other Locations"]/following-sibling::div[1]/p/a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        location_name = "".join(d.xpath(".//text()")).strip()
        if page_url.find("valleyriver") != -1:
            page_url = page_url.replace("valleyriver", "valley-river")
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_type = "<MISSING>"
        ad = "".join(tree.xpath("//p[./span/em]//em/text()"))
        street_address = " ".join(ad.split(",")[0].split()[:-1]).strip()
        phone = "".join(
            tree.xpath('//div[@class="fusion-text fusion-text-7"]//h4[2]//text()')
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].split()[-1].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="fusion-text fusion-text-8"]//span[./strong[text()="CURRENT HOURS"]]/following-sibling::span//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()

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
