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
    locator_domain = "http://mhgas.com"
    page_url = "http://mhgas.com/locations/"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@itemprop="url"]')
    for j in div:
        location_name = "".join(j.xpath('./h3[@itemprop="headline"]/text()'))
        if location_name == "":
            continue
        line = j.xpath('./div[@class="hover-box__content hover-box-content"]/text()')
        line = list(filter(None, [a.strip() for a in line]))
        if len(line) > 3:
            hours_of_operation = line[3:]
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = (
                " ".join(hours_of_operation).replace(" \r\n", "").strip()
            )
        else:
            hours_of_operation = "<MISSING>"
        if hours_of_operation == "<MISSING>":
            hours_of_operation = "".join(
                j.xpath('./h4[@itemprop="alternativeHeadline"]/text()')
            ).strip()
        street_address = "".join(line[0]).strip() or "<MISSING>"
        phone = "".join(line[2]).split(":")[1].strip()
        line = line[1]
        city = line.split()[:-2]
        city = " ".join(city).strip()
        line = line.split()[-2:]
        postal = "".join(line[1]).strip()
        state = "".join(line[0]).strip()
        country_code = "US"
        store_number = location_name.split()[-1].strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

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
