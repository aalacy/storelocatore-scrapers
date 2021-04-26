import csv

from lxml import html
from sgrequests import SgRequests
from sgzip.static import static_zipcode_list, SearchableCountries


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
    s = set()
    url = "https://www.booksamillion.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
    }

    postals = static_zipcode_list(radius=200, country_code=SearchableCountries.USA)
    for p in postals:
        api_url = f"https://www.bullseyelocations.com/pages/BAMStoreFinder?PostalCode={p}&CountryId=1&Radius=500"
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        li = tree.xpath("//ul[@id='resultsCarouselWide']/li")

        for l in li:
            locator_domain = url
            location_name = "".join(l.xpath(".//h3[@itemprop='name']/text()")).strip()
            slug = "".join(l.xpath(".//a[@itemprop='url']/@href")).split("?")[0].strip()
            page_url = f"https://www.bullseyelocations.com/pages/{slug}"
            street_address = "".join(
                l.xpath(".//span[@itemprop='streetAddress']/text()")
            ).strip()
            city = (
                "".join(l.xpath(".//span[@itemprop='addressLocality']/text()")).strip()[
                    :-1
                ]
                or "<MISSING>"
            )
            state = (
                "".join(l.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
                or "<MISSING>"
            )
            postal = (
                "".join(l.xpath(".//span[@itemprop='postalCode']/text()")).strip()
                or "<MISSING>"
            )
            country_code = "US"
            store_number = "".join(
                l.xpath(".//input[@id='ThirdPartyId']/@value")
            ).strip()
            try:
                phone = l.xpath(".//span[@itemprop='telephone']/text()")[0].strip()
            except IndexError:
                phone = "<MISSING>"
            latitude = (
                "".join(l.xpath(".//meta[@itemprop='latitude']/@content"))
                or "<MISSING>"
            )
            longitude = (
                "".join(l.xpath(".//meta[@itemprop='longitude']/@content"))
                or "<MISSING>"
            )
            if latitude == "0" or longitude == "0":
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = (
                "".join(
                    l.xpath(".//div[@class='popDetailsHours']/meta/@content")
                ).replace("|", ";")[:-1]
                or "<MISSING>"
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

            if store_number not in s:
                out.append(row)
                s.add(store_number)
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
