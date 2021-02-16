import csv
from lxml import html
from sgrequests import SgRequests


def write_output(datta):
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

        for row in datta:
            writer.writerow(row)


def get_info(page_url):

    session = SgRequests()
    r = session.post(page_url)
    tree = html.fromstring(r.text)
    phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')).strip()
    text = "".join(tree.xpath("//a/@href"))
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    hours_of_operations = tree.xpath(
        '//h3[contains(text(), "HOURS")]/following-sibling::p[1]/text()'
    )
    hours_of_operations = list(filter(None, [a.strip() for a in hours_of_operations]))
    hours_of_operations = (
        "".join(hours_of_operations).replace("pm", "pm;") or "<MISSING>"
    )
    if hours_of_operations.find("pickup") != -1:
        hours_of_operations = hours_of_operations.split("pickup.")[1]
    return phone, latitude, longitude, hours_of_operations


def fetch_data():
    out = []
    locator_domain = "https://www.mgbwhome.com"
    session = SgRequests()
    countries = ["CA", "US"]

    for country in countries:
        data = {
            "dwfrm_storelocator_country": country,
            "dwfrm_storelocator_findbycountry": "Search",
        }

        r = session.post(
            "https://www.mgbwhome.com/on/demandware.store/Sites-MGBW-Site/en_US/Stores-FindStores",
            data=data,
        )
        tree = html.fromstring(r.text)
        tr = tree.xpath("//table[@id='store-location-results'][1]//tr")
        for t in tr:
            location_name = "".join(t.xpath('.//span[@itemprop="name"]/text()'))
            if location_name == "":
                continue
            street_address = "".join(
                t.xpath('.//span[@itemprop="streetAddress"]/text()')
            ).strip()
            city = (
                "".join(t.xpath('.//span[@itemprop="addressLocality"]/text()'))
                .replace(",", "")
                .strip()
            )
            postal = (
                "".join(t.xpath('.//span[@itemprop="postalCode"]/text()')).strip()
                or "<MISSING>"
            )
            state = "".join(
                t.xpath('.//span[@itemprop="addressRegion"]/text()')
            ).strip()
            page_url = (
                "".join(t.xpath('.//a[@itemprop="url"]/@href')).strip() or "<MISSING>"
            )
            if page_url != "<MISSING>":
                phone, latitude, longitude, hours_of_operation = get_info(page_url)
            else:
                phone, latitude, longitude, hours_of_operation = (
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                )
            if street_address.find("-") != -1 and street_address.find("(") == -1:
                phone = street_address
                street_address = "<MISSING>"
            if page_url.find("Toronto-Signature") != -1:
                session = SgRequests()
                r = session.get(page_url)
                trees = html.fromstring(r.text)
                street_address = (
                    "".join(trees.xpath('//div[@class="grid-span-3"]/text()[2]'))
                    .replace("\n", "")
                    .strip()
                )
            country_code = country
            store_number = "<MISSING>"
            location_type = "<MISSING>"
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
    datta = fetch_data()
    write_output(datta)


if __name__ == "__main__":
    scrape()
