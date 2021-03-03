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
    locator_domain = "https://www.nicolas.com"
    api_url = "https://www.nicolas.com//en/store-finder?q=London&CSRFToken=11159268-fc5a-48b8-bcbb-82518119c5c1"
    session = SgRequests()
    r = session.get(api_url)
    div = (
        r.text.split("data-stores= '")[1]
        .split("'")[0]
        .strip()
        .replace("\n", "")
        .replace("	", "")
    )
    js = json.loads(div)
    for j in js.values():
        location_name = "".join(j.get("displayName")).replace("&#039;", "`")
        street_address = "".join(j.get("address")).replace("&#039;", "`")
        city = "".join(j.get("town"))
        postal = j.get("postcode")
        state = "<MISSING>"
        page_url = "".join(j.get("urlDetail"))
        page_url = f"{locator_domain}{page_url}"
        country_code = j.get("country")
        if country_code.find("France") != -1:
            continue
        store_number = "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = "<MISSING>"
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        phone = " ".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
        hours = tree.xpath('//div[@class="ns-StoreDetails-openingsTimesDetail"]')
        days = tree.xpath('//div[@class="ns-StoreDetails-openingsDay"]//text()')
        days = list(filter(None, [a.strip() for a in days]))
        tmp = []
        _tmp = []
        for h in hours:
            open = (
                "".join(
                    h.xpath(
                        './div[@class="ns-StoreDetails-openingsTimesDetailAM"]/text()'
                    )
                )
                .replace("\n", "")
                .replace("\t", "")
                .strip()
            )
            close = (
                "".join(
                    h.xpath(
                        './div[@class="ns-StoreDetails-openingsTimesDetailPM"]/text()'
                    )
                )
                .replace("\n", "")
                .replace("\t", "")
                .strip()
            )
            line = f"{open}-{close}"
            tmp.append(line)
        closed = (
            "".join(
                tree.xpath(
                    '//div[@class="ns-StoreDetails-openingsTimesDetail ns-StoreDetails-openingsTimesDetail--closed"]/text()'
                )
            )
            .replace("\n", "")
            .replace("\t", "")
            .strip()
        )
        if (
            "".join(
                tree.xpath(
                    '//div[@class="ns-StoreDetails-openingsTimes"]/div[contains(@class, "ns-StoreDetails-openingsTimesDetail ns-StoreDetails-openingsTimesDetail--closed")]/text()'
                )
            )
            .replace("\n", "")
            .replace("\t", "")
            .strip()
            == "Closed"
        ):
            tmp.append(closed)

        for d, t in zip(days, tmp):
            _tmp.append(f"{d.strip()}: {t.strip()}")
        hours_of_operation = ";".join(_tmp) or "<MISSING>"
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
