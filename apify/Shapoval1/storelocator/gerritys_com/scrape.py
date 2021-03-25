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
    locator_domain = "https://gerritys.com"
    api_url = "https://gerritys.com/stores/"
    location_type = "<MISSING>"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://gerritys.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = (
        "".join(tree.xpath('//script[contains(text(), "var stores")]/text()'))
        .replace("\n", "")
        .split("var stores = ")[1]
        .split(";    var postalJson")[0]
    )
    js = json.loads(block)

    for j in js:

        street_address = j.get("address1")
        phone = j.get("phone")
        city = j.get("city")
        postal = j.get("zipCode")
        state = j.get("state")
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "https://gerritys.com/stores/"
        location_name = j.get("name")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        hours = "".join(j.get("hourInfo")).replace("\n", " ")
        if hours.find("Temporary Hours") != -1:
            hours = (
                "".join(j.get("hourInfo"))
                .replace("\n", " ")
                .split("<!--")[1]
                .split("-->")[0]
            )
            hours = html.fromstring(hours)
            hours_of_operation = " ".join(hours.xpath("//*//text()")).strip()
            if hours_of_operation.find("Pharmacy") != -1:
                hours_of_operation = hours_of_operation.split("Pharmacy")[0]
            if hours_of_operation.find("30") != -1:
                hours_of_operation = hours_of_operation.split("30")[1].strip()
            else:
                hours_of_operation = (
                    " ".join(hours.xpath("//*//text()")).split("Pharmacy")[0].strip()
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
