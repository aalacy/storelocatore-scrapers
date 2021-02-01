import csv

from concurrent import futures
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


def get_ids():
    session = SgRequests()
    r = session.get("https://www.frenchconnection.com/store-locator.htm")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@data-store-id]/@data-store-id")


def get_data(_id):
    locator_domain = "https://www.frenchconnection.com/"
    api_url = "https://www.frenchconnection.com/services/storesandstockservice.asmx/GetStoreById"
    data = {"storeId": _id}

    session = SgRequests()
    r = session.post(api_url, data=data)
    tree = html.fromstring(r.content)

    location_name = "".join(tree.xpath("//name/text()"))
    street_address = "".join(tree.xpath("//addressline2/text()")) or "<MISSING>"
    city = "".join(tree.xpath("//addresscity/text()")) or "<MISSING>"
    state = "<MISSING>"
    postal = "".join(tree.xpath("//addresspostcode/text()")) or "<MISSING>"
    country_code = "".join(tree.xpath("//addresscountrycode/text()")) or "<MISSING>"
    store_number = _id
    phone = "".join(tree.xpath("//addressphone/text()")) or "<MISSING>"
    if phone.find("(") != -1:
        phone = phone.split("(")[0].strip()
    if phone.find("EXT") != -1:
        phone = phone.split("EXT")[0].strip()
    latitude = "".join(tree.xpath("//latitude/text()")) or "<MISSING>"
    longitude = "".join(tree.xpath("//longitude/text()")) or "<MISSING>"
    location_type = "".join(tree.xpath("//addressline1/text()")) or "<MISSING>"
    page_url = "https://www.frenchconnection.com/store-locator.htm"
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

    return row


def fetch_data():
    out = []
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
