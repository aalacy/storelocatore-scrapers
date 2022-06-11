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
    locator_domain = "https://www.brotoloc.com/"
    urls = [
        "https://www.brotoloc.com/eau_claire_group_homes.phtml",
        "https://www.brotoloc.com/western_rivers_group_homes.phtml",
        "https://www.brotoloc.com/fox_valley_group_homes.phtml",
    ]

    for page_url in urls:
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        pp = tree.xpath("//p[@class='nomargin']")
        cnt = 1

        for p in pp:
            location_name = "".join(p.xpath("./strong/text()")).strip()

            line = tree.xpath(
                f"//p[@class='nomargin'][{cnt}]/following-sibling::div[1]/p[1]/text()"
            )
            line = list(filter(None, [l.strip() for l in line]))

            if "fox_" not in page_url:
                line = line[0].split("•")
            else:
                line = line[:-1]

            street_address = line[0]
            try:
                phone = line[2].strip()
            except IndexError:
                phone = "<MISSING>"

            line = line[1]
            city = line.split(",")[0].strip()
            line = line.split(",")[1].strip()
            state = line.split()[0]
            postal = line.split()[-1]
            country_code = "US"
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            location_type = "<MISSING>"
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
            cnt += 1

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
