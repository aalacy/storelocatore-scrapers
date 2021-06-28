import csv
from sgrequests import SgRequests
from sgselenium import SgSelenium


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

    locator_domain = "https://redbrickpizza.com/"
    api_url = "https://api.momentfeed.com/v1/analytics/api/v2/llp/sitemap?auth_token=DAVZOMPXNKNHTKET&country=US&multi_account=false"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["locations"]:
        a = j.get("store_info")
        slug = j.get("llp_url")

        page_url = f"https://locations.redbrickpizza.com{slug}"
        location_type = "<MISSING>"
        street_address = f"{a.get('address')} {a.get('address_extended') or ''}".strip()

        state = a.get("region")
        postal = a.get("postcode")
        country_code = "US"
        city = a.get("locality")
        driver = SgSelenium().firefox()
        driver.get(page_url)

        phone = driver.find_element_by_xpath('//div[@itemprop="telephone"]').text
        location_name = "RedBrick Pizza"
        store_number = "<MISSING>"
        latitude = driver.find_element_by_xpath(
            '//meta[@itemprop="latitude"]'
        ).get_attribute("content")
        longitude = driver.find_element_by_xpath(
            '//meta[@itemprop="longitude"]'
        ).get_attribute("content")
        hours_of_operation = driver.find_element_by_xpath(
            '//dl[@itemprop="openingHours"]'
        ).get_attribute("content")

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
        driver.quit()
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
