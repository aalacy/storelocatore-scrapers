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
    locator_domain = "https://orvis.com/"
    api_url = "https://www.orvis.com/on/demandware.store/Sites-USOrvis-Site/en_US/Stores-FindStores?showMap=true&radius=50000%20miles&lat=40.2327&long=-76.9331"
    session = SgRequests()

    r = session.get(api_url)
    js = r.json()
    s = set()
    for j in js["stores"]:

        page_url = (
            j.get("storeLink")
            or "https://www.orvis.com/stores?showMap=true&horizontalView=true&isForm=true"
        )
        location_name = j.get("name") or "<MISSING>"
        street_address = (
            f"{j.get('address1') or ''} {j.get('address2') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("stateCode") or "<MISSING>"
        country_code = j.get("countryCode") or "<MISSING>"

        postal = "".join(j.get("postalCode")) or "<MISSING>"
        if postal.find("-") != -1:
            postal = postal.split("-")[0].strip()
        if not postal.isdigit():
            country_code = "UK"
        store_number = "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = j.get("storeType") or "<MISSING>"
        hours_of_operation = j.get("storeHours") or "<MISSING>"
        if hours_of_operation != "<MISSING>":
            hours_of_operation = html.fromstring(hours_of_operation)
            hours_of_operation = (
                "".join(hours_of_operation.xpath("//*//text()"))
                .replace("\n", "")
                .strip()
            )
        phone = "<MISSING>"
        if (
            page_url
            != "https://www.orvis.com/stores?showMap=true&horizontalView=true&isForm=true"
        ):
            session = SgRequests()
            r = session.get(page_url)
            tree = html.fromstring(r.text)

            phone = (
                "".join(tree.xpath('//h4[@class="phone-number"]/a/text()')).strip()
                or "<MISSING>"
            )
        line = (latitude, longitude)
        if line in s:
            continue
        s.add(line)

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
