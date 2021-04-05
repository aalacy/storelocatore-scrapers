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
    locator_domain = "https://heartlandcoop.com/"
    api_url = "https://heartlandcoop.com/pages/custom.php?id=167"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    td = tree.xpath("//table[@width='756']//td")

    for t in td:

        isvalid = "".join(t.xpath("./p//text()")).strip()
        if not isvalid:
            continue
        line = t.xpath("./p")[-1]
        line = line.xpath("./span//text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[line.index("Heartland Co-op") + 1]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0].strip()
        postal = line.split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        slug = t.xpath(".//a/@href")
        if slug:
            page_url = f"https://heartlandcoop.com{slug[0]}"
            location_name = "".join(t.xpath(".//a//text()")).strip()
        else:
            location_name = "".join(t.xpath(".//h3//text()")).strip()
            if not location_name:
                p = t.xpath("./p")[0]
                location_name = "".join(p.xpath(".//text()")).strip()
                if not location_name:
                    p = t.xpath("./p")[1]
                    location_name = "".join(p.xpath(".//text()")).strip()
            page_url = "<MISSING>"
        phone = (
            t.xpath(".//*[contains(text(), 'Local Phone:')]/text()")[0]
            .replace("Local Phone:", "")
            .strip()
            or "<MISSING>"
        )
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

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
