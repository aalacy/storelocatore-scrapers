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

    locator_domain = "https://www.kitchen1883.com/"
    api_url = "https://www.kitchen1883.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//a[contains(text(), "View Details")] | //a[contains(text(), "Learn More")]'
    )
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("1883") != -1:
            page_url = "https://www.ontherhineeatery.com/find-us"
        if page_url.find("https") == -1:
            page_url = f"https://www.kitchen1883.com{page_url}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        if location_name.find("Find") != -1:
            location_name = "1883 Cafe & Bar"

        location_type = "<MISSING>"
        ad = (
            " ".join(tree.xpath("//h1/following-sibling::div[1]/div/text()"))
            or " ".join(
                tree.xpath(
                    '//div[@class="location__Address-sc-1x5wfjq-0 cAwATM"]/text()'
                )
            )
            .replace("\n", ",")
            .strip()
        )

        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[1].strip()
        store_number = "<MISSING>"

        phone = (
            " ".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
            .replace("\n", "")
            .replace(") ", ")-")
            .strip()
        )
        if phone.find(" ") != -1:
            phone = phone.split()[0].strip()
        hours_of_operation = (
            " ".join(tree.xpath('//*[contains(@class, "Hours")]//text()'))
            .replace("\n", " ")
            .replace("Food Hall Hours", "")
            .strip()
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        session = SgRequests()
        r = session.get(
            "https://www.kitchen1883.com/page-data/index/page-data.json",
            headers=headers,
        )
        js = r.json()["result"]["data"]["locations"]["edges"]
        for j in js:
            loc_name = j.get("node").get("title")
            if loc_name == location_name:
                latitude = j.get("node").get("lat")
                longitude = j.get("node").get("lng")

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
