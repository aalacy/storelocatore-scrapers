import csv
import json
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

    locator_domain = "https://groundround.com"
    api_url = "https://groundround.com/Locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var sites = ")]/text()'))
        .split("var image")[1]
        .split("var sites = ")[1]
        .split("function initialize")[0]
        .replace("];", "]")
    )
    jsblock = jsblock.replace(",	]", "]")
    js = json.loads(jsblock)
    for j in js:
        slug = "".join(j.get("lcontent")).split("a href=")[1].split(">")[0].strip()
        page_url = f"{locator_domain}{slug}"
        location_name = j.get("title")
        location_type = "<MISSING>"
        street_address = "".join(j.get("laddres")).replace("&#39;", "`")
        state = j.get("lstate")
        postal = j.get("lzipe")
        country_code = "US"
        city = j.get("lcity")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = (
            "".join(j.get("lcontent")).split("<h6>")[1].split("</h6>")[0].strip()
        )
        if hours_of_operation.find("temporarily closed") != -1:
            hours_of_operation = "Temporarily closed"
        if hours_of_operation.find("OPENING") != -1:
            hours_of_operation = "Coming Soon"
        if hours_of_operation.find("Temporarily closed") != -1:
            hours_of_operation = "Temporarily closed"
        if (
            hours_of_operation.find("p.m.") == -1
            and hours_of_operation != "Temporarily closed"
            and hours_of_operation != "Temporarily closed"
            and hours_of_operation != "Coming Soon"
        ):
            hours_of_operation = "<MISSING>"
        hours_of_operation = (
            hours_of_operation.replace("Hours:", "")
            .replace("We are open for dine-in & take-out ", "")
            .strip()
        )

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = "".join(
            tree.xpath('//h6[text()="Telephone"]/following-sibling::p[1]//text()')
        )

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
