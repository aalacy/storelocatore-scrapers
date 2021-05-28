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
    locator_domain = "https://pretzelmaker.com"
    page_url = "https://pretzelmaker.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://pretzelmaker.com/locations/",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://pretzelmaker.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
    }
    countries = ["USA", "Canada"]
    for i in countries:
        data = {"locateStore": "true", "country": i}
        session = SgRequests()
        r = session.post(page_url, headers=headers, data=data)
        tree = html.fromstring(r.text)
        jsblock = (
            "".join(tree.xpath('//*[contains(text(), "stores")]//text()'))
            .split("var stores = ")[1]
            .split(";")[0]
        )
        js = json.loads(jsblock)

        for j in js:

            street_address = j.get("sl_address") or "<MISSING>"
            city = "".join(j.get("sl_city")) or "<MISSING>"
            state = j.get("sl_state") or "<MISSING>"
            postal = "".join(j.get("sl_zip")) or "<MISSING>"
            country_code = j.get("sl_country")
            store_number = j.get("sl_id")
            location_name = "".join(j.get("sl_name"))

            if city.find("Charlottetown") != -1:
                state = "PE"
            if city.find("St Albert, AB") != -1:
                city = city.split(",")[0].strip()
                state = "AB"
            if city.find("Windsor, Ontario") != -1:
                city = city.split(",")[0].strip()
                state = "Ontario"
            if city.find("Edmonton") != -1:
                state = "AL"
            if city.find("Bolton") != -1:
                state = "Ontario"
                postal = " ".join(postal.split()[1:]).strip()
            if street_address.find("1570 18th Street") != -1:
                postal = postal.split("MB")[1].strip()
                state = "MB"
            if city.find("Calgary, Alberta") != -1:
                city = city.split(",")[0].strip()
                state = "Alberta"

            if city.find("Halifax") != -1:
                state = "Nova Scotia"
            phone = "".join(j.get("sl_phone")) or "<MISSING>"
            if phone.find("*") != -1:
                phone = "<MISSING>"
            if phone.find("TBD") != -1:
                phone = "<MISSING>"

            latitude = j.get("sl_latitude") or "<MISSING>"
            longitude = j.get("sl_longitude") or "<MISSING>"

            location_type = "<MISSING>"
            if location_name.find("Temporarily Closed") != -1:
                location_type = "Temporarily Closed"
                location_name = location_name.replace(
                    "(Temporarily Closed)", ""
                ).strip()
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
