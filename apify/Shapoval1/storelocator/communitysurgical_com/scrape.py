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

    locator_domain = "https://communitysurgical.com"
    api_url = "https://www.powr.io/map/u/75667338_1547049950#platform=shopify&url=https%3A%2F%2Fcommunitysurgical.com%2Fpages%2Fservicing-locations"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "window.CONTENT")]/text()'))
        .split('"locations":')[1]
        .split(',"smartDesign"')[0]
        .strip()
    )
    jsblock = (
        "["
        + jsblock.replace("[", "").replace("]", "").replace("{", "").replace("}", "")
        + "]"
    )
    jsblock = (
        jsblock.replace('"address"', '["address"')
        .replace(',["address"', '],["address"')
        .replace("/", "")
        .replace("\\", "")
        .replace(":", "")
        .replace('"', "")
    )
    jsblock = jsblock.replace("[[", '[["').replace("],[address", '"],["address')
    jsblock = jsblock + "]"
    jsblock = jsblock.replace("]]", '"]]')
    js = eval(jsblock)

    for i in js:
        page_url = "https://communitysurgical.com/pages/servicing-locations"
        location_name = "".join(i).split("nameu003cpu003e")[1].split(",")[0].strip()
        location_type = "Community Surgical Supply"
        ad = "".join(i).split("address")[1].split("USA")[0].strip()
        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[1].strip()
        store_number = "<MISSING>"
        latitude = "".join(i).split("lat")[1].split(",")[0].strip()
        longitude = "".join(i).split("lng")[1].split(",")[0].strip()
        hours_of_operation = "<MISSING>"
        session = SgRequests()
        r = session.get(
            "https://communitysurgical.com/pages/servicing-locations", headers=headers
        )
        tree = html.fromstring(r.text)
        phone = (
            "".join(tree.xpath('//h1[contains(text(),"Phone")]/text()'))
            .split("Phone:")[1]
            .split("Fax")[0]
            .strip()
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
