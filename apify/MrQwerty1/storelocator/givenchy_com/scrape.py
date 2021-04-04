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


def get_city_to_country_dict(tree):
    out = dict()
    countries = ["us", "ca", "gb"]
    for country in countries:
        cities = tree.xpath(f"//ul[@id='{country}']//a[@data-city]")
        for city in cities:
            key = "".join(city.xpath("./@data-city"))
            out[key] = country.upper()

    return out


def get_hours(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    return (
        ";".join(tree.xpath("//span[@itemprop='openingHours']/text()")) or "<MISSING>"
    )


def fetch_data():
    out = []
    locator_domain = "https://www.givenchy.com/"
    session = SgRequests()
    r = session.get("https://www.givenchy.com/nala/en/storefinder")
    tree = html.fromstring(r.text)
    city_to_country = get_city_to_country_dict(tree)
    city_list = set(city_to_country.keys())
    divs = tree.xpath("//div[@class='store-tile grid-tile col-md-4 col-xs-6']")

    for d in divs:
        store_city = "".join(d.xpath(".//p[@class='store-town']/text()")).strip()
        if store_city not in city_list:
            continue

        location_name = "".join(d.xpath(".//h3[@class='store-name']/text()")).strip()
        street_address = (
            "".join(d.xpath(".//span[@itemprop='streetAddress']/text()")).strip()
            or "<MISSING>"
        )
        city = (
            "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
            or "<MISSING>"
        )
        country_code = city_to_country[store_city]
        if (country_code == "US" or country_code == "CA") and " " in postal:
            state = postal.split()[0]
            postal = " ".join(postal.split()[1:])
        else:
            state = "<MISSING>"

        store_number = "".join(d.xpath("./@itemid"))
        page_url = f"https://www.givenchy.com/nala/en/store?StoreID={store_number}"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel:')]/@href")).replace("tel:", "")
            or "<MISSING>"
        )
        latitude = "".join(d.xpath(".//span[@data-lat]/@data-lat")) or "<MISSING>"
        longitude = "".join(d.xpath(".//span[@data-lat]/@data-lng")) or "<MISSING>"
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
