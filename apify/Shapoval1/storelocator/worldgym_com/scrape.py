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

    locator_domain = "https://www.worldgym.com"
    api_url = "https://www.worldgym.com/findagym?search=ca"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(
            tree.xpath('//script[contains(text(), "var franhiseeLocations")]/text()')
        )
        .split("var franhiseeLocations = ")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(jsblock)

    for j in js:

        page_url = j.get("MicroSiteUrl")
        location_name = j.get("LocationName")
        location_type = "GYM"
        street_address = f"{j.get('Line1')} {j.get('Line2')}".strip()
        state = j.get("State")
        postal = j.get("Postal")
        country_code = j.get("Country")
        if country_code != "USA" and country_code != "Canada":
            continue
        city = j.get("City")
        store_number = "".join(j.get("LocationNumber")).replace("WGY", "").strip()
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        phone = j.get("PhoneWithOutCountryCode")

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[contains(@class, "tab-pane gymhourstab")]//h5//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[./div/h2[text()="HEURES"]]/following-sibling::div[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        hours_of_operation = (
            hours_of_operation.replace("LUNDI", "MONDAY")
            .replace("MARDI", "TUESDAY")
            .replace("MERCREDI", "WEDNESDAY")
            .replace("JEUDI", "THURSDAY")
            .replace("VENDREDI", "FRIDAY")
            .replace("SAMDI", "SATURDAY ")
            .replace("DIMANCHE", "SUNDAY")
            .replace("SAMEDI", "SATURDAY")
            .replace("À", "TO")
        )
        if hours_of_operation.find("Taille") != -1:
            hours_of_operation = hours_of_operation.split("Taille")[0].strip()

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
