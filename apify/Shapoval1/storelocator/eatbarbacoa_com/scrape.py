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

    locator_domain = "https://www.eatbarbacoa.com"
    page_url = "https://www.eatbarbacoa.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@data-block-json, "location")]')
    for d in div:
        location_type = "<MISSING>"
        location_name = (
            "".join(d.xpath(".//following-sibling::div[1]//h2//text()"))
            .replace("\n", "")
            .strip()
        )
        page_url = (
            "".join(d.xpath(".//following-sibling::div[1]//h2/a/@href"))
            .replace("\n", "")
            .strip()
            or "https://www.eatbarbacoa.com/locations"
        )
        if page_url.find("https://www.eatbarbacoa.com") == -1:
            page_url = f"{locator_domain}{page_url}"
        phone = (
            "".join(d.xpath(".//following-sibling::div[1]//p/text()[3]"))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone.find("!") != -1:
            phone = phone.split("!")[1].strip()

        jsblock = "[" + "".join(d.xpath(".//@data-block-json")) + "]"
        js = json.loads(jsblock)
        for j in js:
            a = j.get("location")
            street_address = a.get("addressLine1")
            ad = "".join(a.get("addressLine2")).replace("UT,", "UT").strip()
            if location_name.find("Inlet Beach") != -1:
                ad = (
                    "".join(d.xpath(".//following-sibling::div[1]//p/text()[2]"))
                    .replace("\n", "")
                    .strip()
                )

            city = ad.split(",")[0].strip()
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[-1].strip()
            country_code = a.get("addressCountry")
            store_number = "<MISSING>"
            latitude = a.get("mapLat")
            longitude = a.get("mapLng")
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
