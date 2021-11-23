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

    locator_domain = "https://www.georgerichards.ca"
    page_url = "https://www.georgerichards.ca/apps/store-finder"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "markersCoords")]/text()'))
        .split("'You Are Here';")[1]
        .split("function initialize()")[0]
        .replace("markersCoords.push(", "")
        .replace(");", ",")
        .strip()
    )
    jsblock = jsblock.replace("{", '["').replace("}", '"]').replace(":", " ")
    jsblock = eval(jsblock)

    for j in jsblock:

        idd = "".join(j).split("id")[1].split(",")[0].strip()
        page_url = "https://www.georgerichards.ca/apps/store-finder"
        location_name = "".join(j).split("name&#039;&gt;")[1].split("&lt;")[0].strip()
        latitude = "".join(j).split("lat")[1].split(",")[0].strip()
        longitude = "".join(j).split("lng")[1].split(",")[0].strip()

        session = SgRequests()
        r = session.get(
            f"https://stores.boldapps.net/front-end/get_store_info.php?shop=georgerichards-storefront.myshopify.com&data=detailed&store_id={idd}",
            headers=headers,
        )
        js = r.json()["data"]
        a = html.fromstring(js)
        location_type = "George Richards"
        street_address = (
            "".join(a.xpath('//span[@class="address"]/text()'))
            .replace("\n", "")
            .strip()
            + " "
            + "".join(a.xpath('//span[@class="address2"]/text()'))
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(a.xpath('//span[@class="phone"]/text()')).replace("\n", "").strip()
        )
        state = (
            "".join(a.xpath('//span[@class="prov_state"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        postal = (
            "".join(a.xpath('//span[@class="postal_zip"]/text()'))
            .replace("\n", "")
            .strip()
        )
        city = (
            "".join(a.xpath('//span[@class="city"]/text()')).replace("\n", "").strip()
        )
        country_code = "CA"
        store_number = (
            "".join(a.xpath('//span[@class="custom_field_value"]/text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(a.xpath('//span[@class="hours"]/text()')).replace("\n", "").strip()
        )
        if store_number.find("Temporarily Closed") != -1:
            store_number = store_number.split("Temporarily Closed")[0].strip()
            hours_of_operation = "Temporarily Closed"

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
