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

    locator_domain = "https://gooseheadinsurance.com/"

    api_url = "https://agents.gooseheadinsurance.com/index.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="Directory-listLinks"]/li/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        sub_page_url = f"https://agents.gooseheadinsurance.com/{slug}"
        if (
            sub_page_url.find(
                "https://agents.gooseheadinsurance.com/id/coeur-d'-alene/1500-northwest-blvd"
            )
            != -1
        ):
            sub_page_url = "https://agents.gooseheadinsurance.com/id"
        if (
            sub_page_url.find(
                "https://agents.gooseheadinsurance.com/nv/henderson/150-n-stephanie-street"
            )
            != -1
        ):
            sub_page_url = "https://agents.gooseheadinsurance.com/nv"
        session = SgRequests()
        r = session.get(sub_page_url, headers=headers)
        tree = html.fromstring(r.text)
        ul = tree.xpath('//a[@class="Directory-listLink"]')
        for l in ul:
            sslug = "".join(l.xpath(".//@href"))
            page_url = f"https://agents.gooseheadinsurance.com/{sslug}"
            if page_url.count("/") < 5:
                session = SgRequests()
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                ul = tree.xpath('//a[@class="Teaser-titleLink"]')
                for l in ul:
                    sslug = "".join(l.xpath(".//@href"))
                    page_url = f"https://agents.gooseheadinsurance.com/{sslug}".replace(
                        "../", ""
                    )
            if (
                page_url.find(
                    "https://agents.gooseheadinsurance.com/id/coeur-d'-alene/1500-northwest-blvd"
                )
                != -1
            ):
                page_url = "https://agents.gooseheadinsurance.com/id/coeur-d%27-alene/1500-northwest-blvd"
            if (
                page_url.find(
                    "https://agents.gooseheadinsurance.com/il/o'fallon/784-wall-street"
                )
                != -1
            ):
                page_url = "https://agents.gooseheadinsurance.com/il/o%27fallon/784-wall-street"
            if (
                page_url.find(
                    "https://agents.gooseheadinsurance.com/mo/lee's-summit/4967b-ne-goodview-cir"
                )
                != -1
            ):
                page_url = "https://agents.gooseheadinsurance.com/mo/lee%27s-summit/4967b-ne-goodview-cir"

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            location_name = "".join(
                tree.xpath('//div[@class="Core-miniBio Core-hidden--xs"]/h1/text()')
            ).strip()
            location_type = "<MISSING>"

            street_address = (
                "".join(tree.xpath('//span[@class="c-address-street-1"]/text()'))
                + " "
                + "".join(tree.xpath('//span[@class="c-address-street-2"]/text()'))
                or "<MISSING>"
            )
            latitude = (
                "".join(
                    tree.xpath(
                        '//span[@class="coordinates"]/meta[@itemprop="latitude"]/@content'
                    )
                )
                or "<MISSING>"
            )
            longitude = (
                "".join(
                    tree.xpath(
                        '//span[@class="coordinates"]/meta[@itemprop="longitude"]/@content'
                    )
                )
                or "<MISSING>"
            )
            country_code = "US"
            state = (
                "".join(tree.xpath('//abbr[@class="c-address-state"]/text()'))
                or "<MISSING>"
            )
            postal = (
                "".join(tree.xpath('//span[@class="c-address-postal-code"]/text()'))
                or "<MISSING>"
            )
            city = (
                "".join(tree.xpath('//span[@class="c-address-city"]/text()'))
                or "<MISSING>"
            )
            store_number = "<MISSING>"
            hours_of_operation = (
                " ".join(tree.xpath('//table[@class="c-hours-details"]//tr/td//text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "Closed"
            phone = (
                "".join(
                    tree.xpath(
                        '//div[text()="CONTACT"]/following-sibling::div[2]//div[@itemprop="telephone"]/text()'
                    )
                )
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
