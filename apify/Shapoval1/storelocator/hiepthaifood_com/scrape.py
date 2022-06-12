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

    locator_domain = "http://www.hiepthaifood.com/"
    page_url = "http://www.hiepthaifood.com/contact-us.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//span[@style="font-size:26px;"]')
    for d in div:

        location_name = "".join(d.xpath(".//text()"))
        location_type = "Food Store"
        street_address = "".join(d.xpath(".//following::p[1]//text()"))
        ad = "".join(d.xpath(".//following::p[2]//text()"))

        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        slug = street_address.split()[0].strip()
        ll = (
            "".join(
                d.xpath(
                    f'.//following::script[contains(text(), "{slug}")]/text() | .//preceding::script[contains(text(), "{slug}")]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        latitude = ll.split("lat:")[1].split(",")[0].strip()

        longitude = ll.split("lng:")[1].split("}")[0].strip()
        phone = (
            "".join(d.xpath(".//following::p[4]//text()")).replace("Tel:", "").strip()
        )
        hours_of_operation = (
            "".join(d.xpath(".//following::p[7]//text()"))
            .replace("Hours:", "")
            .replace("\n", "")
            .replace("​   ", "")
            .replace(": 00", ":00")
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
