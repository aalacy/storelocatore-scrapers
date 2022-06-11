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

    locator_domain = "https://www.stewleonards.com/"
    api_url = "https://www.stewleonards.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="locations mobile"]//button[contains(text(), "location details")]'
    )
    for d in div:
        page_url = (
            "".join(d.xpath("./@onclick"))
            .split("self.location='")[1]
            .split("'")[0]
            .strip()
        )
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h1[@class="boogaloo green caps"]/text()'))
            .replace("STORE LOCATION & HOURS", "")
            .strip()
        )

        location_type = "<MISSING>"
        street_address = (
            "".join(
                tree.xpath(
                    '//h2[contains(text(), "Store Location")]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )

        ad = (
            "".join(
                tree.xpath(
                    '//h2[contains(text(), "Store Location")]/following-sibling::text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(
                tree.xpath(
                    '//h2[contains(text(), "Store Location")]/following-sibling::text()[3]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if street_address.find("Paramus") != -1:
            street_address = (
                street_address
                + " "
                + "".join(
                    tree.xpath(
                        '//h2[contains(text(), "Store Location")]/following-sibling::text()[2]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            ad = (
                "".join(
                    tree.xpath(
                        '//h2[contains(text(), "Store Location")]/following-sibling::text()[3]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            phone = (
                "".join(
                    tree.xpath(
                        '//h2[contains(text(), "Store Location")]/following-sibling::text()[4]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        text = "".join(tree.xpath('//div[@class="column two-thirds"]/a/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            elif text.find("rllag=") != -1:
                latitude = (
                    text.split("rllag=")[1].split(",")[0].replace("41", "41,").strip()
                )
                longitude = (
                    text.split("rllag=")[1].split(",")[1].replace("-73", "-73,").strip()
                )
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = "Open 7 Days 8am-9pm"

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
