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

    locator_domain = "https://www.askitalian.co.uk"
    api_url = "https://www.askitalian.co.uk/wp-json/locations/get_venues"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["data"]:
        page_url = j.get("link")

        location_name = "".join(j.get("title"))
        location_type = "<MISSING>"
        ad = "".join(j.get("address"))

        street_address = ad.split("\n")[0].strip()
        phone = j.get("phone_number") or "<MISSING>"
        state = "".join(j.get("region")).replace(",", "")
        postal = ad.split("\n")[-1].strip()
        country_code = "UK"
        city = ad.split("\n")[1].replace(",", "").strip()

        store_number = "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        openToday = tree.xpath('//p[@class="c-opening-times__today"]/span/text()')
        openToday = list(filter(None, [a.strip() for a in openToday]))
        openToday = " ".join(openToday)

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="c-opening-times__tables-holder"]//tr/td/text()'
                )
            )
            .replace("\n", "")
            .strip()
            + " "
            + openToday
        )
        if location_name.find("Temporarily Closed") != -1:
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
