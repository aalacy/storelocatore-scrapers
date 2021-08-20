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

    locator_domain = "https://pizzatime.com/"
    api_url = "https://pizzatime.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(text(), "ORDER NOW")]')

    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        datas = (
            "".join(
                d.xpath(
                    './/preceding::a[contains(@href, "tel")][1]/preceding-sibling::text()'
                )
            )
            .split(",")[1]
            .replace("Seatac", "SeaTac")
            .strip()
        )
        latitude = "".join(
            d.xpath(f'.//following::div[@data-title="{datas}"]/@data-lat')
        )
        longitude = "".join(
            d.xpath(f'.//following::div[@data-title="{datas}"]/@data-lng')
        )
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath(
                '//div[contains(@class, "et_pb_section et_pb_section_0")]//h2//text()'
            )
        )
        location_type = "<MISSING>"
        street_address = (
            "".join(tree.xpath('//div[./h4/span[text()="Address"]]/div/text()[1]'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(tree.xpath('//div[./h4/span[text()="Address"]]/div/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        phone = "".join(
            tree.xpath(
                '//h4[./a[contains(@href, "tel")]]/following-sibling::div//text() | //h4[./span[contains(text(), "Phone")]]/following-sibling::div/text()'
            )
        )
        if phone.find("for") != -1:
            phone = phone.split("for")[0].strip()

        state = ad.split(",")[1].split()[0].strip()
        try:
            postal = ad.split(",")[1].split()[1].strip()
        except:
            postal = "<MISSING>"
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath('//div[./h4/span[text()="Hours"]]/div/text()'))
            .replace("\n", "")
            .replace("|", "")
            .replace("&", "-")
            .strip()
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
