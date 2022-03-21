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
        slug = page_url.split("/")[-1].replace("_", ".").replace("-", "+")

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Authorization": "DAVZOMPXNKNHTKET",
            "Origin": "https://locations.redbrickpizza.com",
            "Connection": "keep-alive",
            "Referer": "https://locations.redbrickpizza.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "TE": "trailers",
        }
        r = session.get(
            f"https://api.momentfeed.com/v1/analytics/api/llp.json?address={slug}&locality={city}&multi_account=false&pageSize=30&region={state}",
            headers=headers,
        ).json()
        js = r[0]

        phone = js.get("store_info").get("phone")
        location_name = js.get("store_info").get("name")
        store_number = "<MISSING>"
        latitude = js.get("store_info").get("latitude")
        longitude = js.get("store_info").get("longitude")
        hours_of_operation = "".join(js.get("store_info").get("hours"))
        if hours_of_operation.find("1,") == -1 and hours_of_operation.find("2,") == -1:
            hours_of_operation = "1,Closed;2,Closed " + hours_of_operation

        hours_of_operation = (
            hours_of_operation.replace("1,", "Monday ")
            .replace("2,", "Tuesday ")
            .replace("3,", "Wednesday ")
            .replace("4,", "Thursday ")
            .replace("5,", "Friday ")
            .replace("6,", "Saturday ")
            .replace("7,", "Sunday ")
        )
        hours_of_operation = (
            hours_of_operation.replace("30", ":30")
            .replace(",", " - ")
            .replace("00", ":00")
            .replace(":000", "0:00")
        )
        cms = js.get("open_or_closed")
        if cms == "coming soon":
            hours_of_operation = "Coming Soon"
        if hours_of_operation != "Coming Soon":
            hours_of_operation = hours_of_operation[:-1].strip()

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
