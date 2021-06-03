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

    locator_domain = "https://www.solidcore.co"
    api_url = "https://www.solidcore.co/studios/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var locations =")]/text()'))
        .split("var locations =")[1]
        .split(";")[0]
        .replace("[", "")
        .replace("]", "")
        .strip()
    )
    jsblock = (
        jsblock.replace("lat", '"lat"')
        .replace("lng", '"lng"')
        .replace("icon", '"icon"')
        .replace("infoWindow", '"infoWindow"')
        .replace("content", '"content"')
        .replace("\n", "")
    )
    jsb = eval(jsblock)
    for i in jsb:
        latitude = i.get("lat")
        longitude = i.get("lng")
        info = i.get("infoWindow").get("content")
        info = html.fromstring(info)
        page_url = "https://www.solidcore.co" + "".join(
            info.xpath("//p/strong/a/@href")
        )
        location_name = "".join(info.xpath("//p/strong/a/text()"))
        location_type = "gym"
        street_address = "".join(info.xpath("//p[./strong/a]/text()[1]"))
        ad = "".join(info.xpath("//p[./strong/a]/text()[2]")).replace("\n", "").strip()
        phone = (
            "".join(info.xpath("//p[./strong/a]/text()[3]")).replace("\n", "").strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
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
