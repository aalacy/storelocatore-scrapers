import csv
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
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
    locator_domain = "https://orvis.com/"
    api_url = "https://stores.orvis.com/"
    session = SgRequests()

    r = session.get(api_url)

    tree = html.fromstring(r.text)
    block = tree.xpath(
        '//option[contains(text(), "Select a State")]/following-sibling::option'
    )
    for b in block:
        slug = "".join(b.xpath(".//@value"))
        page_url = f"https://stores.orvis.com{slug}"
        session = SgRequests()

        r = session.get(page_url)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="OSL-results-column-wrapper"]')
        for d in div:

            location_name = "".join(d.xpath('.//h4[@class="margin-bottom-5"]//text()'))
            ad = d.xpath(".//p[@class='margin-bottom-10']//text()")
            ad = list(filter(None, [a.strip() for a in ad]))
            ad = " ".join(ad)
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            if street_address.find("#3 Fm 2673") != -1:
                street_address = "1642 FM 2673 #3"
            if location_name.find("San Antonio Orvis Retail Store") != -1:
                street_address = "Park North Shopping Center"
            city = a.city or "<MISSING>"
            state = a.state or "<MISSING>"
            country_code = "US"
            postal = a.postcode or "<MISSING>"
            if postal == "00000":
                postal = "<MISSING>"
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = (
                " ".join(d.xpath('.//div[@class="OSL-hour-line"]/div/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            phone = (
                "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
            )
            if phone.find("(toll free)") != -1:
                phone = phone.split("(toll free)")[0].strip()
            if phone.find("(Mark)") != -1:
                phone = phone.split("(Mark)")[0].strip()
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
