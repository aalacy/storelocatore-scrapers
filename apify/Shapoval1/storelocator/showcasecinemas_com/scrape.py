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

    locator_domain = "https://www.showcasecinemas.com"
    api_url = "https://www.showcasecinemas.com/theaters"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "pc.cinemas")]/text()'))
        .split("pc.cinemas = ")[1]
        .split(";")[0]
        .replace("false", "False")
        .strip()
    )
    js = eval(jsblock)
    for j in js:
        slug = j.get("CinemaInfoUrl")
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(j.get("CinemaName"))
        location_type = "Showcase Cinema"
        street_address = j.get("Address1")
        state = j.get("StateCode")
        postal = j.get("ZipCode")
        country_code = "USA"
        city = j.get("City")
        store_number = "<MISSING>"
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"

        session = SgRequests()
        r = session.get("https://www.showcasecinemas.com/contact-us", headers=headers)
        tree = html.fromstring(r.text)
        loc_name = tree.xpath("//ul/li/strong")
        for l in loc_name:
            l_name = "".join(l.xpath(".//text()")).capitalize()
            if l_name.find(" ") != -1:
                l_name = l_name.split()[0].capitalize().strip()
            if l_name == "N.":
                l_name = "North"
            if location_name.find(l_name) != -1:
                phone = "".join(l.xpath(".//following-sibling::a//text()"))

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
