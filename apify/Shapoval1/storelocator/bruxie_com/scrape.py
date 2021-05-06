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
    locator_domain = "https://bruxie.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "*/*",
        "Accept-Language": "en-US",
        "Referer": "https://order.online/sl/bruxie--the-original-fried-chicken-and-waffle-sandwich-48317/en-US",
        "content-type": "application/json",
        "X-Experience-Id": "storefront",
        "X-Channel-Id": "marketplace",
        "apollographql-client-name": "@doordash/app-consumer-production",
        "apollographql-client-version": "0.441.0-production",
        "X-CSRFToken": "",
        "Origin": "https://order.online",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }

    data = '{"operationName":"allBusinessStores","variables":{"businessId":"2554"},"query":"query allBusinessStores($businessId: ID!) {\\n businessInfo(businessId: $businessId) {\\n stores {\\n id\\n name\\n address {\\n id\\n city\\n subpremise\\n printableAddress\\n state\\n street\\n country\\n lat\\n lng\\n shortname\\n zipCode\\n __typename\\n }\\n offersPickup\\n offersDelivery\\n __typename\\n }\\n __typename\\n }\\n}\\n"}'

    r = session.post("https://order.online/graphql", headers=headers, data=data)
    js = r.json()
    for j in js["data"]["businessInfo"]["stores"]:
        a = j.get("address")
        page_url = "https://bruxie.com/"

        street_address = "".join(a.get("street"))
        city = a.get("city")
        state = a.get("state")
        postal = a.get("zipCode")
        location_name = j.get("name")
        country_code = a.get("country")
        store_number = "<MISSING>"
        latitude = a.get("lat")
        longitude = a.get("lng")
        location_type = "<MISSING>"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[contains(text(), "HOURS OF OPERATION")]/following-sibling::div/ul/li/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = " ".join(
            tree.xpath('//span[contains(@aria-label, "Phone")]/text()')
        ).replace(") ", ")-")
        if street_address.find("215") != -1:
            phone = phone.split()[0].strip()
        if street_address.find("292") != -1:
            phone = phone.split()[1].strip()
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
