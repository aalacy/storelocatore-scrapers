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

    locator_domain = "https://www.badboy.ca/"

    api_url = "https://www.badboy.ca/find-a-store"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "jsonLocations")]/text()'))
        .split("jsonLocations:")[1]
        .split("imageLocations:")[0]
        .replace('"currentStoreId":"1"},', '"currentStoreId":"1"}')
        .replace('/div> "},', '/div> "}')
    )

    jsblock = (
        jsblock.split('"block":"')[1]
        .replace('"}', "")
        .replace("\\", "")
        .replace("> <", "><")
        .strip()
    )

    block = html.fromstring(jsblock)
    div = block.xpath("//a")
    for d in div:

        page_url = "".join(d.xpath(".//@href")).strip()
        if page_url.find("https") == -1:
            page_url = f"{locator_domain}{page_url}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        phone = (
            "".join(tree.xpath('//div[@class="store_phone"]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        ad = (
            "".join(tree.xpath('//div[@class="store_address"]/text()'))
            .replace("\n", "")
            .replace("Canada  225", "Canada Ontario")
            .replace(", ,", ",")
            .strip()
        )

        location_name = (
            "".join(tree.xpath('//div[@class="store_contact_info-inner"]/h3[1]/text()'))
            or "<MISSING>"
        )
        if page_url.find("ottawa") != -1:
            location_name = "Ottawa Store"
        location_type = "Lastman's Bad Boy"
        street_address = ad.split(",")[0].strip()
        country_code = "Canada"
        try:
            state = ad.split(",")[2].split()[-3].strip()
        except:
            state = ad.split(",")[3].split()[-3].strip()
        postal = " ".join(ad.split(",")[2].split()[-2:]).strip()
        city = ad.split(",")[1].strip()
        if ad.count(",") == 3:
            street_address = street_address + " " + ad.split(",")[1].strip()
            city = ad.split(",")[2].strip()
            postal = " ".join(ad.split(",")[3].split()[-2:]).strip()
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="opening_hours"]/text()'))
            .replace("\n", "")
            .replace(" (", " ")
            .replace(") ", " ")
            .strip()
            or "<MISSING>"
        )

        latitude = (
            "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
            .split("LatLng(")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
            .split("LatLng(")[1]
            .split(",")[1]
            .split(")")[0]
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
