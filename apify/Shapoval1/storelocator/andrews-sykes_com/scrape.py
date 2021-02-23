import csv
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


def get_data():
    rows = []
    locator_domain = "https://www.andrews-sykes.com"
    api_url = "https://www.andrews-sykes.com/fetchLocations/"
    session = SgRequests()

    r = session.get(api_url)
    cccv = ""
    for cookie in r.cookies:
        cv = cookie.value
        cccv += cv

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.andrews-sykes.com",
        "Connection": "keep-alive",
        "Referer": "https://www.andrews-sykes.com/locations/?__cf_chl_captcha_tk__=fd4103f392ad2de390b6fe91f2be7958fbcc6f99-1613155972-0-AQNidLSzdUGtfrIpJqUiz45ndRcrlhAVZau3u9o0MDh-483qC7aL-bxRJ4_7GQiZIZ3GyG4RfOknBtHzuFeSCm8_I7GLWdcl4h0ez7-dVHsTC8AlJj6TyzcIxLEHgyREFFr0ozdSwZnqOrXVsWO2URq_IFBym7D3FMiewOoeDCft8AFqErJjQ8ZJJk6mVJHGvF0OipJARvGSKXkbPd0USJ_FdKY4n36-QQgoijAgIfnXycfmhoxtEreQMifpQdz42hR46mr7uSORdVhG7lHGbLMzN_MMFqhL9MLbZxlQVy25f7CzE_SILqdqxJiTrcpUXLhoyLJqNDSHu2jrRhkHhPVLn_cizj9m_GfFRm9ZbZgP0KW95H01UQ1JtPomxb74Zgz6eQSL0K0mJX3ILDiyNQj2cURK_rUaZDtrvYnzOHmWkeCT0ApqKOxKyQgEnibRBpA96aAAhRq8sjQnNTTbJf_7ttbsJATgtH_i-ngNCEE9GglFcY7h0jqB7qbQqsCkrh8M4J_yy12LjkK37Nhxkt2avJwTRjtWUEtVLtLPBeuP",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }

    cookies = {"__cfduid": cccv}

    r = session.post(api_url, headers=headers, cookies=cookies)
    js = r.json()
    for j in js:
        street_address = "".join(j.get("streetAddress")) or "<MISSING>"
        city = "".join(j.get("addressLocality")) or "<MISSING>"
        state = "".join(j.get("addressRegion")) or "<MISSING>"
        postal = "".join(j.get("postalCode")) or "<MISSING>"
        country_code = "".join(j.get("Country")) or "<MISSING>"
        if country_code != "United Kingdom":
            continue
        store_number = "<MISSING>"
        location_name = "".join(j.get("name")) or "<MISSING>"
        if location_name == "Sedgefield":
            continue
        phone = "".join(j.get("telephone")) or "<MISSING>"
        page_url = "https://www.andrews-sykes.com/locations/"
        latitude = "".join(j.get("latitude")) or "<MISSING>"
        longitude = "".join(j.get("longitude")) or "<MISSING>"
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

        rows.append(row)
    return rows


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
