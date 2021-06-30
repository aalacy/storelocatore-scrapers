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
    locator_domain = "https://pizzanova.com"
    api_url = "https://pizzanova.com/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//option[contains(text(), "Please")]/following-sibling::option')
    for b in block:
        slug = "".join(b.xpath(".//@value"))
        if slug.find(" ") != -1:
            slug = slug.replace(" ", "_")
        page_url = f"https://pizzanova.com/store-locator/?city={slug}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="location-information"]')
        for d in div:
            location_name = "<MISSING>"
            street_address = "".join(d.xpath(".//h2/text()"))
            phone = "<MISSING>"
            city = page_url.split("=")[1]
            state = "<MISSING>"
            country_code = "CA"
            store_number = "<MISSING>"
            ll = "".join(
                d.xpath('//preceding::script[contains(text(), "var PNStores")]/text()')
            )
            latitude = (
                ll.split(street_address)[1]
                .split("]")[0]
                .replace('",', "")
                .strip()
                .split(",")[0]
            )
            longitude = (
                ll.split(street_address)[1]
                .split("]")[0]
                .replace('",', "")
                .strip()
                .split(",")[1]
            )
            location_type = "<MISSING>"
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/strong[contains(text(), "HOURS OF OPERATION:")]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            postal = "<MISSING>"

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
