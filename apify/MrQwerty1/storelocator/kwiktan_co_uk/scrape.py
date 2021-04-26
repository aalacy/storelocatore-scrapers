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


def get_hours(page_url):
    _tmp = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    li = tree.xpath("//h4[text()='Opening Times']/following-sibling::ul/li")
    for l in li:
        day = "".join(l.xpath("./div[1]//text()")).strip()
        time = (
            " ".join("".join(l.xpath("./div[2]//text()")).split())
            .replace("CLOSED -", "Closed")
            .replace("*", "")
        )
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://www.kwiktan.co.uk/"
    api_url = "https://www.kwiktan.co.uk/salon-finder/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'var singleSalonTitle;')]/text()")
    )
    for t in text.split("new Array();")[1:]:
        j = dict()
        for cell in t.split("\n")[:-1]:
            key = cell.split("'")[1]
            val = cell.split("'")[3]
            j[key] = val

        street_address = j.get("Street") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        state = "<MISSING>"
        postal = j.get("Postcode") or "<MISSING>"
        country_code = "GB"
        store_number = "<MISSING>"
        page_url = j.get("Url")
        location_name = j.get("Title").replace("&#8211;", "-")
        phone = j.get("Number") or "<MISSING>"
        latitude = j.get("Lat") or "<MISSING>"
        longitude = j.get("Lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = get_hours(page_url)

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
