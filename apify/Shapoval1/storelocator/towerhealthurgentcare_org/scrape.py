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

    locator_domain = "https://towehealthurgentcare.org"

    for i in range(3):

        api_url = f"https://towerhealth.org/locations?f%5B0%5D=services%3Aurgent%20care&page={i}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath(
            '//div[contains(@class, "teaser location js-section-animation")]//h2[@class="teaser__name"]/a'
        )
        for d in div:
            slug = "".join(d.xpath(".//@href"))
            page_url = f"{locator_domain}{slug}"
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            location_name = "".join(
                tree.xpath('//h1[@class="location-hero__title"]/text()')
            )
            location_type = "Urgent care"
            ad = tree.xpath(
                '//span[contains(text(), "Address")]/following-sibling::span/text()'
            )
            street_address = "".join(ad[0])
            if len(ad) > 2:
                street_address = street_address + " " + "".join(ad[1])
            adr = "".join(ad[-1])
            phone = "".join(
                tree.xpath(
                    '//span[contains(text(), "Main")]/following-sibling::*/text()'
                )
            )
            state = adr.split(",")[1].split()[0].strip()
            postal = adr.split(",")[1].split()[1].strip()
            country_code = "US"
            city = adr.split(",")[0].strip()
            store_number = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = (
                " ".join(tree.xpath('//ul[@class="hours-block__days"]/li//text()'))
                .replace("\n", "")
                .replace("   ", " ")
                .strip()
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
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
