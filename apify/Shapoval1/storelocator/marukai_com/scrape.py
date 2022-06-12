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

    locator_domain = "https://marukai.com/"
    api_url = "https://marukai.com/pages/all-locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//table//tr")

    for d in div:

        location_name = "".join(d.xpath(".//td[1]//text()")).replace("\n", "").strip()
        location_type = "Marukai Market"
        ad = "".join(d.xpath(".//td[2]/p/text()")).replace("\n", "").strip()
        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        hours_of_operation = (
            " ".join(d.xpath(".//td[4]/p/text()")).replace("\n", "").strip()
        )
        if hours_of_operation.find("Senior") != -1:
            hours_of_operation = hours_of_operation.split("Senior")[0].strip()
        phone = "".join(d.xpath(".//td[3]/p/text()")).replace("\n", "").strip()
        country_code = "USA"
        city = ad.split(",")[1].strip()
        page_url = "".join(d.xpath(".//td[5]/p/a/@href"))
        store_number = "<MISSING>"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        map_link = "".join(tree.xpath('//div[@class="rte"]/iframe[1]/@src')) or "".join(
            tree.xpath('//div[@class="rte"]/p/iframe[1]/@src')
        )
        if street_address.find("8125") != -1:
            map_link = "".join(tree.xpath('//div[@class="rte"]/iframe[2]/@src'))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
