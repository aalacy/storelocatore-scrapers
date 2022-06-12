import csv
import json
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
    locator_domain = "https://www.belmond.com"
    api_url = "https://www.belmond.com/north-america/usa"

    session = SgRequests()
    r = session.get(api_url)
    block = r.text.split('portfoliodata="')[1].split('">')[0].replace("&#034;", '"')
    js = json.loads(block)

    for j in js["portfolioProducts"]:
        slug = "".join(j.get("url"))
        if slug.find("usa") == -1:
            continue

        page_url = f"{locator_domain}{slug}"
        location_name = j.get("name")
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        ad = (
            "".join(tree.xpath('//p[./strong[contains(text(), "Address")]]/text()'))
            .replace("·", "")
            .replace("USA", "")
            .replace("California,", "California")
            .strip()
        )

        street_address = ad.split(",")[0].strip()
        city = ad.split(",")[1].strip()
        state = " ".join(ad.split(",")[2].split()[:-1]).strip()
        postal = ad.split(",")[2].split()[-1].strip()
        phone = (
            "".join(tree.xpath('//p[./strong[contains(text(), "Phone")]]//text()'))
            .replace("·", "")
            .replace("Phone", "")
            .strip()
        )

        country_code = "US"
        store_number = "<MISSING>"
        location_type = page_url.split("belmond.com/")[1].split("/")[0]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
