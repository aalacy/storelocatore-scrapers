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

    locator_domain = "https://lightcinemas.co.uk/"
    api_url = "https://wisbech.lightcinemas.co.uk/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    jsblock = (
        "".join(
            tree.xpath(
                '//script[contains(text(), "new Glitterfish.ChangeCinema")]/text()'
            )
        )
        .split("2, ")[1]
        .split(", false);")[0]
        .strip()
    )
    js = json.loads(jsblock)

    for j in js:

        page_url = j.get("url") + "/your-cinema/map"
        location_name = j.get("title")
        store_number = j.get("id")
        if page_url == "https://sittingbourne.thelight.co.uk/your-cinema/map":
            page_url = "https://sittingbourne.thelight.co.uk/"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = "".join(tree.xpath('//p[@class="address"]/strong/text()[1]')) or "".join(
            tree.xpath('//p[@class="address"]/text()')
        )

        location_type = "Cinema"
        street_address = ad.split(",")[0].strip()
        if ad.count(",") == 3:
            street_address = " ".join(ad.split(",")[:2]).strip()
        state = "<MISSING>"
        postal = ad.split(",")[-1].strip()
        country_code = "UK"
        city = (
            page_url.split("//")[1]
            .split(".")[0]
            .capitalize()
            .strip()
            .replace("New", "New ")
            .replace("brighton", "Brighton")
        )
        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "<MISSING>"
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
