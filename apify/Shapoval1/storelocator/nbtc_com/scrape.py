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

    locator_domain = "https://nbtc.com"

    session = SgRequests()
    r = session.get("https://nbtc.com/locations/")
    tree = html.fromstring(r.text)
    key = (
        "".join(tree.xpath('//link[@rel="preload"]/@href'))
        .split("static/")[1]
        .split("/")[0]
        .strip()
    )

    api_url = f"https://nbtc.com/_nuxt/static/{key}/locations/payload.js"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    block = (
        r.text.split("branches:")[1].split(",fetch:[]")[0].replace("}]}]", "}]").strip()
    )
    block = (
        block.replace("id:", '"id":')
        .replace("title", '"title"')
        .replace("branchTileLabel", '"branchTileLabel"')
        .replace("apartmentOrSuite", '"apartmentOrSuite"')
        .replace("city", '"city"')
        .replace("state", '"state"')
        .replace("zipcode", '"zipcode"')
        .replace("streetAddress", '"streetAddress"')
    )
    block = (
        block.replace("latitude", '"latitude"')
        .replace("longitude", '"longitude"')
        .replace("phoneNumber", '"phoneNumber"')
        .replace("url:", '"url":')
    )
    block = (
        block.replace(":Q", ':"Q"')
        .replace(":R", ':"R"')
        .replace(":S", ':"S"')
        .replace(":T", ':"T"')
        .replace(":U", ':"U"')
        .replace(":V", ':"V"')
    )
    block = (
        block.replace(":W", ':"W"')
        .replace(":X", ':"X"')
        .replace(":Y", ':"Y"')
        .replace(":x", ':"x"')
        .replace(":a", ':"a"')
        .replace(":c", ':"c"')
        .replace(":y", ':"y"')
    )
    js = eval(block)
    for j in js:

        page_url = j.get("url")
        location_name = j.get("title")
        location_type = "Branch"
        street_address = j.get("streetAddress")
        phone = j.get("phoneNumber")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        country_code = "US"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = (
            " ".join(
                tree.xpath(
                    '//h6[text()="Branch Address"]/following-sibling::div//text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        city = ad.split(",")[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        store_number = "<MISSING>"
        hours_of_operation = tree.xpath(
            '//h6[contains(text(), "Branch Hours")]/following-sibling::div/p/text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = (
            " ".join(hours_of_operation)
            .replace("\n", "")
            .replace("              ", " ")
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
