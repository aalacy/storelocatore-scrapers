import csv
from sgrequests import SgRequests
from lxml import html


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


def get_rows(url):
    rows = []

    session = SgRequests()
    r = session.get(url)

    tree = html.fromstring(r.text)
    li = tree.xpath("//li[@data-shopid]")
    locator_domain = "https://www.badcock.com/"
    for l in li:
        location_name = "".join(l.xpath(".//a[@class='shop-link']/text()")).strip()
        store_number = location_name.split("(")[1].replace(")", "").strip()
        if location_name.lower().find("coming") != -1:
            continue
        page_url = "https://www.badcock.com" + "".join(
            l.xpath(".//a[@class='shop-link']/@href")
        )
        line = l.xpath(".//div[@class='short-description']/p[not(./strong)]/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[0]
        line = line[1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        phone = "".join(
            l.xpath(".//p[./strong[contains(text(), 'Phone')]]/text()")
        ).strip()
        latitude = "".join(
            l.xpath(".//input[@class='shop-coordinates']/@data-latitude")
        )
        longitude = "".join(
            l.xpath(".//input[@class='shop-coordinates']/@data-longitude")
        )
        location_type = "<MISSING>"

        _tmp = []
        hours = l.xpath(
            ".//p[./strong and  ./strong[not(contains(text(),'Phone'))] and ./strong[not(contains(text(),'Fax'))]]"
        )
        for h in hours:
            day = "".join(h.xpath("./strong/text()")).strip()
            time = "".join(h.xpath("./text()")).strip()

            _tmp.append(f"{day} {time}")

        hours_of_operation = "; ".join(_tmp) or "<MISSING>"
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
        rows.append(row)

    return rows


def fetch_data():
    out = []
    urls = [
        "https://www.badcock.com/allshops",
        "https://www.badcock.com/StoreLocator/GetRemainingShops",
    ]

    for u in urls:
        out += get_rows(u)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
