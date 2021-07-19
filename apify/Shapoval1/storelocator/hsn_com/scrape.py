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

    locator_domain = "https://www.hsn.com"
    api_url = "https://www.hsn.com/content/HSN_Outlet/261#"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h3[@class="_38821_h3"]')
    for d in div:

        page_url = "https://www.hsn.com/content/HSN_Outlet/261#"
        location_name = "".join(d.xpath(".//text()"))
        location_type = "outlet"
        ad = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[1]"))
            .replace("\n", "")
            .strip()
        )
        if location_name.find("Bardmoor") != -1:
            ad = (
                "".join(d.xpath(".//following-sibling::p[1]/text()[2]"))
                .replace("\n", "")
                .strip()
            )
        ad = ad.replace("FL 34654", "FL, 34654").replace("FL.", "FL")
        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[2].strip()
        postal = ad.split(",")[3].strip()
        country_code = "US"
        city = ad.split(",")[1].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        if location_name.find("Bardmoor") != -1:
            phone = (
                "".join(d.xpath(".//following-sibling::p[1]/text()[3]"))
                .replace("\n", "")
                .strip()
            )
        hours_of_operation = (
            " ".join(d.xpath(".//following-sibling::p[1]/text()"))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = hours_of_operation.split("Hours of Operation:")[1].strip()
        if hours_of_operation.find("and") != -1:
            hours_of_operation = hours_of_operation.split("and")[0].strip()

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
