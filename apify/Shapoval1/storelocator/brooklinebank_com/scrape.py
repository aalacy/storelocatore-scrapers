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


def get_urls():
    session = SgRequests()
    r = session.get("https://brooklinebank.com/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//td/h3/a/@href")


def fetch_data():
    out = []
    session = SgRequests()
    locator_domain = "https://brooklinebank.com/"
    slugs = get_urls()

    for slug in slugs:
        page_url = f"{locator_domain}{slug}"
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        amount = len(
            tree.xpath("//div[@id='subpage-content']/div[@class='col-md-12' and .//h4]")
        )

        for i in range(amount):
            d = tree.xpath("//div[@id='subpage-content']/div[@class='col-md-12']")[i]
            table = tree.xpath("//div[@id='subpage-content']/div[@class='col-md-12']")[
                i
            ].xpath("./following-sibling::table[1]")[0]

            location_name = "".join(d.xpath("./div/h4/text()")).strip()
            if page_url.find("chestnut") != -1:
                location_name = "".join(d.xpath("./h4/text()")).strip()
            line = d.xpath("./div[@class='col-md-5']/p[1]/text() | ./p[1]/text()")
            line = list(filter(None, [l.strip() for l in line]))

            street_address = "".join(line[1])
            if page_url.find("boston") != -1 and street_address.find("31") == -1:
                street_address = "".join(line[0])
            if location_name.find("Brookline") != -1:
                street_address = "".join(line[0])
            if street_address.find("131") != -1:
                location_name = "".join(
                    d.xpath("./h4[@class='col-md-4']/text()")
                ).strip()
            city = "".join(tree.xpath("//title/text()")).split("-")[-1].strip()
            state = "MA"
            postal = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            phone = line[-1]
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            location_type = "<MISSING>"

            _tmp = []
            tr = table.xpath(".//tr/following-sibling::tr")
            for t in tr:
                day = " ".join("".join(t.xpath("./td[1]//text()")).split())
                start = " ".join("".join(t.xpath("./td[2]//text()")).split())
                close = " ".join(
                    "".join(t.xpath("./td[3]//text() | ./td[4]//text()")).split()
                )
                _tmp.append(f"{day}: {start} - {close}")

            hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
