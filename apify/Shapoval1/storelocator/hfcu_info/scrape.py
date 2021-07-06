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

    locator_domain = "https://www.hfcu.info"
    page_url = "https://www.hfcu.info/about-us/locations-and-hours"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="listbox"]')
    for d in div:
        location_name = "".join(d.xpath('.//span[@class="cuname"]/a/text()')).strip()

        adr = d.xpath('.//span[@class="cuname"]/following-sibling::p//text()')
        location_type = "<MISSING>"
        street_address = "".join(adr[0]).strip()
        ad = "".join(adr[1]).strip()
        phone = "".join(adr[3]).strip()
        if phone.find("MYCU") != -1:
            phone = phone.replace("MYCU ", "").strip()
        if phone.find("Ext") != -1:
            phone = phone.split("Ext")[0]
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        try:
            ll = (
                "".join(
                    d.xpath('.//following::script[contains(text(), "LatLng")]/text()')
                )
                .split(location_name)[1]
                .split("'getDir(")[1]
                .split(");'")[0]
            )
        except IndexError:
            ll = (
                "".join(
                    d.xpath('.//following::script[contains(text(), "LatLng")]/text()')
                )
                .split(location_name)[2]
                .split("'getDir(")[1]
                .split(");'")[0]
            )
        latitude = ll.split(",")[0].strip()
        longitude = ll.split(",")[1].strip()
        hours_of_operation = d.xpath(
            './/p[./u[contains(text(), "Lobby")]]//text() | .//h3[contains(text(), "Hours")]/following-sibling::p//text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
        if hours_of_operation.find("Lobby") != -1:
            hours_of_operation = hours_of_operation.split("Lobby")[1].split(
                "Drive-Thru"
            )[0]
        hours_of_operation = (
            hours_of_operation.replace(":", "")
            .replace("Drive-Thru Only", "")
            .replace("Available after hours by appointment.", "")
            .replace("30", ":30")
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
