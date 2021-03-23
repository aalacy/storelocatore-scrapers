import csv
import yaml

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


def get_root(_id):
    session = SgRequests()
    r = session.get(
        f"https://stores.boldapps.net/front-end/get_store_info.php?shop=rocky-mountain-chocolate-factory.myshopify.com&data=detailed&store_id={_id}"
    )
    source = r.json()["data"]

    return html.fromstring(source)


def remove_comma(text):
    if text.endswith(","):
        return text[:-1]
    return text


def fetch_data():
    out = []
    locator_domain = "https://rockychoc.com/"
    page_url = "https://rockychoc.com/apps/store-locator/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'markersCoords.push(')]/text()")
    )
    text = text.split("markersCoords.push(")[1:]
    for t in text:
        _id = t.split("id:")[1].split(",")[0].strip()
        if _id == "0":
            break

        j = yaml.load(t.split(", id")[0] + "}", Loader=yaml.Loader)
        root = get_root(_id)

        street_address = "".join(root.xpath("//span[@class='address']/text()")).strip()
        city = remove_comma("".join(root.xpath("//span[@class='city']/text()")).strip())
        state = "".join(root.xpath("//span[@class='prov_state']/text()")).strip()
        postal = remove_comma(
            "".join(root.xpath("//span[@class='postal_zip']/text()")).strip()
        )
        country_code = "CA"
        store_number = "<MISSING>"
        location_name = "".join(root.xpath("//span[@class='name']/text()")).strip()
        if location_name.find("(") != -1:
            location_name = location_name.split("(")[0].strip()

        phone = "".join(root.xpath("//span[@class='phone']/text()")).strip()
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
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
