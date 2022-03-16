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

    locator_domain = "https://www.honda.co.uk"
    for link in [
        "https://www.honda.co.uk/cars/dealer-list.html",
        "https://www.honda.co.uk/motorcycles/dealer-list.html",
        "https://www.honda.co.uk/marine/dealer-list.html",
    ]:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(link, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//td[@class="wrapperInner"]')
        s = set()
        for d in div:
            slug = "".join(d.xpath(".//a/@href"))

            page_url = f"{locator_domain}{slug}"
            if (
                page_url
                == "https://www.honda.co.uk/cars/dealers/glyn-hopkin-romford.html"
                or page_url == "https://www.honda.co.uk/cars/dealers/STA463.html"
                or page_url == "https://www.honda.co.uk/motorcycles/dealers/CHM100.html"
                or page_url == "https://www.honda.co.uk/marine/dealers/MIX001.html"
                or page_url == "https://www.honda.co.uk/marine/dealers/PSL001.html"
                or page_url == "https://www.honda.co.uk/cars/dealers/DON342.html"
            ):
                continue
            session = SgRequests()
            r = session.get(page_url, headers=headers)

            tree = html.fromstring(r.text)

            location_name = "".join(tree.xpath('//div[@class="dealer-name"]/h1/text()'))

            location_type = "<MISSING>"
            street_address = tree.xpath('//span[@itemprop="streetAddress"]//text()')
            street_address = list(filter(None, [a.strip() for a in street_address]))
            street_address = (
                "".join(street_address)
                .replace("\n", "")
                .replace("                    ", "")
            )
            phone = (
                "".join(
                    tree.xpath(
                        '//div[./h2[contains(text(), "Sales")]]/following-sibling::div[1]//a[contains(@href, "tel")]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if phone == "<MISSING>":
                phone = (
                    "".join(
                        tree.xpath(
                            '//div[./h2[contains(text(), "Service")]]/following-sibling::div[1]//a[contains(@href, "tel")]/text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
            phone = phone.replace("Option 1", "").strip()
            state = (
                "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()'))
                or "<MISSING>"
            )
            postal = (
                "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
                or "<MISSING>"
            )
            country_code = "UK"
            city = (
                "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
                or "<MISSING>"
            )
            store_number = "<MISSING>"
            text = "".join(tree.xpath('//div[@class="dealer-map"]/a/@href'))
            try:
                if text.find("ll=") != -1:
                    latitude = text.split("ll=")[1].split(",")[0]
                    longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
                else:
                    latitude = text.split("@")[1].split(",")[0]
                    longitude = text.split("@")[1].split(",")[1]
            except IndexError:
                latitude, longitude = "<MISSING>", "<MISSING>"

            hours_of_operation = tree.xpath(
                '//div[./h2[contains(text(), "Sales")]]/following-sibling::div[2]//text()'
            )
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
            if hours_of_operation == "<MISSING>":
                hours_of_operation = tree.xpath(
                    '//div[./h2[contains(text(), "Service")]]/following-sibling::div[2]//text()'
                )
                hours_of_operation = list(
                    filter(None, [a.strip() for a in hours_of_operation])
                )
                hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"

            line = (latitude, longitude, street_address)
            if line in s:
                continue

            s.add(line)

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
