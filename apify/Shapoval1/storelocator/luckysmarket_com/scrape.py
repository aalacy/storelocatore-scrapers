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
    locator_domain = "https://www.luckysmarket.com/"
    api_url = "https://www.luckysmarket.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[./div/div/p[contains(text(), "STORES")]]/following-sibling::ul/li/a'
    )

    for d in div:
        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("https://www.luckysmarket.com/store-tour") != -1:
            continue
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//span[@style="font-size:52px"]//text()'))
        street_address = "".join(
            tree.xpath(
                '//p[.//span[contains(text(), "ADDRESS")]]/following-sibling::p[1]//text()'
            )
        )
        ad = "".join(
            tree.xpath(
                '//p[.//span[contains(text(), "ADDRESS")]]/following-sibling::p[2]//text()'
            )
        )

        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        country_code = "US"
        postal = ad.split(",")[1].split()[1].strip()
        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[.//span[contains(text(), "HOURS")]]/following-sibling::p//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Daily") != -1:
            hours_of_operation = hours_of_operation.split("Daily")[1].strip()
        phone = "".join(
            tree.xpath(
                '//p[.//span[contains(text(), "PHONE")]]/following-sibling::p[1]//text()'
            )
        )
        api_url2 = "https://api.freshop.com/1/stores?app_key=luckys_market&has_address=true&limit=10&token=697fa5ec06c7d44dc5ac93d07b4ab5ac"
        session = SgRequests()
        r = session.get(api_url2, headers=headers)
        js = r.json()["items"]
        for j in js:
            adr = j.get("address_1")
            if adr == street_address:
                latitude = j.get("latitude")
                longitude = j.get("longitude")
                store_number = j.get("store_number")

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
