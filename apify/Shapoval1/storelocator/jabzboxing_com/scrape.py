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

    locator_domain = "https://www.jabzboxing.com"
    api_url = "https://www.jabzboxing.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//h4/following-sibling::ul/li/a")
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h1[@class="f-med large_dark"]/text()'))
            .replace("\n", "")
            .strip()
        )

        location_type = "<MISSING>"
        street_address = (
            "".join(tree.xpath('//h4[@class="f-30 m-text"]/a/text()[1]')).strip()
            or "<MISSING>"
        )
        ad = (
            "".join(tree.xpath('//h4[@class="f-30 m-text"]/a/text()[2]'))
            .replace("\n", "")
            .strip()
        )

        phone = "".join(tree.xpath('//h3[@class="f-med"]/a/text()')) or "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "US"
        city = "<MISSING>"
        if ad != ",":
            city = ad.split(",")[0].strip()
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[-1].strip()
        if (
            page_url.find("https://www.jabzboxing.com/locations/Drexel-Hill,-PA") != -1
            or page_url.find("https://www.jabzboxing.com/locations/Tampa,-FL") != -1
        ):
            state = page_url.split("-")[-1]
        if (
            location_name.find("Bel Air, MD") != -1
            or location_name.find("Midland, TX") != -1
        ):
            city = location_name.split(",")[0].strip()
            state = location_name.split(",")[1].strip()
        store_number = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if location_name.find(",") != -1:
            hours_of_operation = "COMING SOON"
        ll = (
            "".join(
                tree.xpath(
                    '//script[contains(text(), "center: new google.maps.LatLng")]/text()'
                )
            )
            or "<MISSING>"
        )

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if ll != "<MISSING>":
            latitude = ll.split("LatLng(")[1].split(",")[0]
            longitude = ll.split("LatLng(")[1].split(",")[1].split(")")[0]
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
