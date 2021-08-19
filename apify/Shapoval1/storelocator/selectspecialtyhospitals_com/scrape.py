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

    locator_domain = "https://www.selectspecialtyhospitals.com/"
    api_url = "https://www.selectspecialtyhospitals.com//sxa/search/results/?s={A9835FD2-AE76-4383-876E-44128806F6A6}|{A9835FD2-AE76-4383-876E-44128806F6A6}&itemid={9DE36713-213C-446D-A694-DEC9AC996203}&sig=&autoFireSearch=true&v={E695F09C-8569-4B59-8EA8-F89CEF8FE995}&p=1000"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["Results"]

    for j in js:
        cont = j.get("Html")
        a = html.fromstring(cont)
        page_url = "".join(a.xpath('//div[@class="loc-result-card-name"]/a/@href'))
        location_name = "".join(
            a.xpath('//div[@class="loc-result-card-name"]/a/text()')
        )
        location_type = "Regency Hospital"
        if page_url.find("regencyhospital") != -1:
            location_type = "Regency Hospital"
        if page_url.find("selectspecialtyhospitals") != -1:
            location_type = "Select Specialty Hospital"
        street_address = "".join(
            a.xpath('//a[contains(@href, "maps")]/text()[1]')
        ).strip()

        ad = (
            "".join(a.xpath('//a[contains(@href, "maps")]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        phone = "".join(
            a.xpath(
                '//span[text()="PHONE"]/following-sibling::a[contains(@href, "tel")]/text()'
            )
        ).strip()
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        ll = "".join(a.xpath('//a[contains(@href, "maps")]/@href'))
        latitude = ll.split("=")[2].split(",")[0].strip()
        longitude = ll.split(",")[-1].strip()
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
