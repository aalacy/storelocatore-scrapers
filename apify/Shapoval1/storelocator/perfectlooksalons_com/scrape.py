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

    locator_domain = "https://www.perfectlooksalons.com/"
    api_url = "https://www.perfectlooksalons.com/apps/store-locator"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "markersCoords.push")]/text()'))
        .split("'You Are Here';")[1]
        .split("function")[0]
        .replace("markersCoords.push(", "")
        .replace(");", ",")
        .strip()
    )
    div = div.replace("{", '["').replace("}", '"]').replace(":", "")
    div = eval(div)

    for d in div:

        page_url = "https://www.perfectlooksalons.com/apps/store-locator"
        location_name = "".join(d).split("name&#039;&gt;")[1].split("&lt;")[0].strip()
        location_type = "Perfect look salons"
        street_address = (
            "".join(d).split("address&#039;&gt;")[1].split("&lt;")[0].strip()
        )
        state = "".join(d).split("prov_state&#039;&gt;")[1].split("&lt;")[0].strip()
        postal = "".join(d).split("postal_zip&#039;&gt;")[1].split("&lt;")[0].strip()
        city = "".join(d).split("city&#039;&gt;")[1].split("&lt;")[0].strip()
        country_code = "United States"
        store_number = "".join(d).split("id")[1].split(",")[0].strip()
        latitude = "".join(d).split("lat")[1].split(",")[0].strip()
        longitude = "".join(d).split("lng")[1].split(",")[0].strip()
        session = SgRequests()
        r = session.get(
            f"https://stores.boldapps.net/front-end/get_store_info.php?shop=perfect-look-salons.myshopify.com&data=detailed&store_id={store_number}",
            headers=headers,
        )
        js = r.json()
        info = js.get("data")
        info = html.fromstring(info)
        phone = "".join(info.xpath('//span[@class="phone"]/text()')).strip()
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
