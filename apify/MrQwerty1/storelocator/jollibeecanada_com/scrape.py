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
    locator_domain = "http://jollibeecanada.com/"
    page_url = "http://jollibeecanada.com/store-locator/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='storeindicont']")

    for d in divs:
        lines = d.xpath("./p[1]/text()")
        lines = list(filter(None, [l.strip() for l in lines]))

        i = 0
        for l in lines:
            if l.startswith("("):
                break
            i += 1

        phone = lines[i]
        street_address = ", ".join(lines[: i - 1])
        hours_of_operation = ";".join(lines[i + 1 :]).replace("Hours:", "").strip()
        if hours_of_operation.startswith(";"):
            hours_of_operation = hours_of_operation[1:]
        lines = lines[i - 1]
        if lines.find(",") == -1:
            city = lines.split()[0].strip()
            state = lines.split()[1].strip()
        else:
            city = lines.split(",")[0].strip()
            state = lines.split(",")[1].strip().split()[0]
            if len(state) != 2:
                state = "<MISSING>"
        postal = lines.replace(city, "").replace(state, "").replace(",", "").strip()
        country_code = "CA"
        store_number = "<MISSING>"
        location_name = "".join(d.xpath("./h4/text()")).strip()
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
