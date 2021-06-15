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
    locator_domain = "https://www.sysco.com"
    api_url = "https://www.sysco.com/Contact/Contact/Our-Locations.html"

    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "const locations")]/text()'))
        .split("const locations = ")[1]
        .split(";")[0]
    )
    js = json.loads(jsblock)
    js = tuple(js)
    for j in js:
        if j == {}:
            continue
        jso = json.loads(json.dumps(j))
        for i in jso.values():

            street_address = i.get("street") or "<MISSING>"
            city = i.get("city") or "<MISSING>"
            postal = i.get("zip") or "<MISSING>"
            state = i.get("state") or "<MISSING>"
            if (
                city.find("45134 Zapopan, Jalisco") != -1
                or city.find("22215 Tijuana, Baja California") != -1
                or city.find("66367 Santa Catarina, Nuevo Leon") != -1
            ):
                ad = city
                city = ad.split(",")[0].split()[-1].strip()
                postal = ad.split()[0].strip()
                state = ad.split(",")[1].strip()
            if city.find("Aldermaston, Berkshire") != -1:
                ad = city
                city = ad.split(",")[0].strip()
                state = ad.split(",")[1].strip()
            if state == "0":
                state = "<MISSING>"
            country_code = i.get("country") or "<MISSING>"
            store_number = "<MISSING>"
            location_name = "/" + i.get("@path") or "<MISSING>"
            location_name = location_name.replace("//", "").replace("/", " ").strip()
            phone = i.get("mainPhone") or "<MISSING>"
            latitude = i.get("lat") or "<MISSING>"
            longitude = i.get("lng") or "<MISSING>"
            location_type = i.get("locationType") or "<MISSING>"
            hours_of_operation = i.get("customerServiceHours") or "<MISSING>"
            page_url = (
                i.get("websiteUrl")
                or "https://www.sysco.com/Contact/Contact/Our-Locations.html"
            )
            if "sysco.com" not in page_url:
                page_url = "https://www.sysco.com/Contact/Contact/Our-Locations.html"

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
