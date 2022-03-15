import csv
from sgrequests import SgRequests
from concurrent import futures


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


def get_urls():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Origin": "https://brusters.com",
        "Connection": "keep-alive",
        "Referer": "https://brusters.com/",
    }
    session = SgRequests()
    r = session.get(
        "https://brusters.azurewebsites.net/API/AutoCompleteListJson.aspx",
        headers=headers,
    )
    js = r.json()["results"]
    out = []
    for j in js:
        postal = j.get("zip")
        url = f"https://brusters.azurewebsites.net/API/StoreSearchJson.aspx?search={postal}"
        out.append(url)
    return out


def get_data(url):
    rows = []
    locator_domain = "https://brusters.com"
    api_url = "".join(url)

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Origin": "https://brusters.com",
        "Connection": "keep-alive",
        "Referer": "https://brusters.com/",
    }
    r = session.get(api_url, headers=headers)
    try:
        js = r.json()["results"]
    except:
        return []
    for j in js:
        page_url = j.get("master_url")

        location_name = "".join(j.get("store_name"))
        street_address = "".join(j.get("address"))
        store_number = j.get("store_number")
        if location_name.find("I'm sorry") != -1:
            continue
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "US"

        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = "<MISSING>"
        days = ["mon", "tue", "wed", "thur", "fri", "sat", "sun"]
        tmp = []
        for d in days:
            days = d
            opens = j.get(f"{d}_open")
            closes = j.get(f"{d}_close")
            line = f"{days} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"
        if hours_of_operation.count("Temporarily Closed") == 14:
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
        rows.append(row)
    return rows


def fetch_data():
    out = []
    s = set()
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[8]
                if _id not in s:
                    s.add(_id)
                    out.append(row)
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
