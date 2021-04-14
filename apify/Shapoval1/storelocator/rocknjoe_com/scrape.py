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

    locator_domain = "https://www.rocknjoe.com"
    page_url = "https://www.rocknjoe.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./a[contains(@href, "facebook")]]')

    for d in div:

        location_type = "<MISSING>"
        street_address = "".join(d.xpath(".//preceding-sibling::div[./p]/p[1]//text()"))
        ad = "".join(d.xpath(".//preceding-sibling::div[./p]/p[2]//text()"))
        phone = "".join(d.xpath(".//preceding-sibling::div[./p]/p[3]//text()"))
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        location_name = "".join(d.xpath(".//preceding-sibling::div/h6//text()"))
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        tmpcls = "".join(
            d.xpath(
                './/following-sibling::div[5]/p/span[contains(text(), "Temporarily Closed")]/text()'
            )
        )
        _tmp = []
        days = "<MISSING>"
        times = "<MISSING>"
        if not tmpcls:
            days = d.xpath(".//following-sibling::div[4]/p//text()")
            days = list(filter(None, [a.strip() for a in days]))

            times = d.xpath(".//following-sibling::div[5]/p//text()")
            times = list(filter(None, [a.strip() for a in times]))
        if days != "<MISSING>" and times != "<MISSING>":
            for d, t in zip(days, times):
                _tmp.append(f"{d.strip()}: {t.strip()}")

        hours_of_operation = " ".join(_tmp)
        if tmpcls:
            hours_of_operation = "Temporarily Closed"

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
