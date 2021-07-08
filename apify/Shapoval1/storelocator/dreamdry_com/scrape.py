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

    locator_domain = "https://dreamdry.com"
    page_url = "https://dreamdry.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p[./a[contains(@href, "tel")]]')
    for d in div:

        location_name = "".join(d.xpath(".//preceding::h1[1]/text()"))
        location_type = "<MISSING>"
        ad = d.xpath(".//a[1]/text()")
        street_address = "".join(ad[0])
        if len(ad) > 2:
            street_address = "".join(ad[0]) + " " + "".join(ad[1])
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        street_address = street_address.replace("Powers Ferry Square", "").strip()
        adr = "".join(ad[-1]).replace("NY,", "NY")

        state = adr.split(",")[1].split()[0].strip()
        postal = adr.split(",")[1].split()[1].strip()
        country_code = "US"
        city = adr.split(",")[0].strip()
        store_number = "<MISSING>"
        text = "".join(d.xpath(".//a[1]/@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "".join(d.xpath(".//a[2]/text()"))
        hours_of_operation = "<MISSING>"

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
