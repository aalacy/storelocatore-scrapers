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

    locator_domain = "https://www.healthyplanetcanada.com"
    api_url = "https://www.healthyplanetcanada.com/amlocator/index/ajax/"

    session = SgRequests()
    cookies = {
        "__cfduid": "d966e654a602e8f69032771d3179be51d1617296895",
        "cf_clearance": "8b8a16feb52156e8e08a16610148cda67ebcba70-1617301592-0-250",
        "nostojs": "autoload",
        "2c.cId": "6065fdf060b2da98ee50f66f",
        "_hjTLDTest": "1",
        "_hjid": "07dc70e7-565d-4af9-bc58-bcc987cb150f",
        "_fbp": "fb.1.1617296881508.1100096458",
        "form_key": "UrDxYv4h1AMjHlwb",
        "_hjIncludedInPageviewSample": "1",
        "_ga": "GA1.2.2098145768.1617296883",
        "_gid": "GA1.2.851525939.1617296883",
        "private_content_version": "a736febad67c468465b020c6cd6e834f",
        "cf_chl_2": "9a40c595628e1fa",
        "cf_chl_prog": "a23",
        "_hjAbsoluteSessionInProgress": "0",
        "mage-cache-storage": "%7B%7D",
        "mage-cache-storage-section-invalidation": "%7B%7D",
        "recently_viewed_product": "%7B%7D",
        "recently_viewed_product_previous": "%7B%7D",
        "recently_compared_product": "%7B%7D",
        "recently_compared_product_previous": "%7B%7D",
        "product_data_storage": "%7B%7D",
        "_gat": "1",
        "mage-messages": "",
        "PHPSESSID": "ptdo923sghjnrf8s9l5dik5gj7",
        "X-Magento-Vary": "5d0a030364fbb1422a987684403b70877671a5b4",
        "section_data_ids": "%7B%22rewards%22%3A1617301626%2C%22personal-data%22%3A1617301625%7D",
        "_uetsid": "cfcafef0930c11eba146d7e51297e083",
        "_uetvid": "cfcadf20930c11eb8a85e541e0604979",
        "mage-cache-sessid": "true",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.healthyplanetcanada.com",
        "Connection": "keep-alive",
        "Referer": "https://www.healthyplanetcanada.com/storelocator/",
    }

    data = {
        "lat": "0",
        "lng": "0",
        "radius": "",
        "product": "0",
        "category": "0",
        "attributes[0][name]": "4",
        "attributes[0][value]": "",
        "attributes[1][name]": "3",
        "attributes[1][value]": "",
        "sortByDistance": "1",
    }

    r = session.post(api_url, headers=headers, data=data, cookies=cookies)
    js = r.json()
    for j in js["items"]:
        line = j.get("popup_html")
        line = html.fromstring(line)
        page_url = (
            "".join(line.xpath('//a[@class="amlocator-link"]/@href'))
            .replace(" /", "")
            .replace(")/", "")
        )

        street_address = (
            "".join(line.xpath("//div/text()"))
            .split("Address:")[1]
            .split("State:")[0]
            .strip()
        )
        city = (
            "".join(line.xpath("//div/text()"))
            .split("City:")[1]
            .split("Zip:")[0]
            .strip()
        )
        state = (
            "".join(line.xpath("//div/text()"))
            .split("State:")[1]
            .split("Description:")[0]
            .strip()
        )
        postal = (
            "".join(line.xpath("//div/text()"))
            .split("Zip:")[1]
            .split("Address:")[0]
            .strip()
        )
        hours_of_operation = (
            "".join(js.get("block")).split(street_address)[1].split("(")[0]
        )
        hours_of_operation = html.fromstring(hours_of_operation)
        hours_of_operation = (
            " ".join(
                hours_of_operation.xpath(
                    '//div[@class="amlocator-schedule-table"]/div/span/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        country_code = "CA"
        store_number = "<MISSING>"
        location_name = "".join(line.xpath('//a[@class="amlocator-link"]/@title'))
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        phone = "<INACCESSIBLE>"

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
