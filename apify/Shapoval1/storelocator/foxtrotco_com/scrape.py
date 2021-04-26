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
    locator_domain = "https://foxtrotco.com"
    lol = [1, 2, 3]
    for i in lol:
        api_url = f"https://api.foxtrotchicago.com/v5/retail-stores/?region_id={i}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "TE": "Trailers",
        }
        cookies = {
            "regionId": "1",
            "ajs_anonymous_id": "%22b7da7825-775a-4ce9-beb0-487dabf70ec1%22",
            "_pin_unauth": "dWlkPU1tTmlabVkxTURBdE1XTTNPUzAwTm1NekxXRXpZell0TXpnNE1ESmxZbUl3TVdaag",
            "_ga": "GA1.2.295328351.1614322962",
            "_gid": "GA1.2.2040120576.1614322962",
            "_fbp": "fb.1.1614322962942.1461945517",
            "exitIntentCookie": "true",
            "shipShopRegionId": "1",
            "_gali": "city",
        }
        r = session.get(api_url, headers=headers, cookies=cookies)
        js = r.json()["stores"]
        for j in js:
            street_address = j.get("address")
            city = j.get("city")
            postal = j.get("zip")
            state = "".join(j.get("state"))
            country_code = "US"
            store_number = "<MISSING>"
            location_name = "".join(j.get("name"))
            location_type = "<MISSING>"
            if state.find("DC") != -1:
                location_type = "Coming Soon"
            phone = j.get("phone")
            latitude = j.get("lat")
            slug = location_name.replace(" ", "-").lower()
            page_url = f"https://foxtrotco.com/stores/{slug}"
            longitude = j.get("lon")

            hours = j.get("operating_hours")
            tmp = []
            days = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            for h in hours:
                day = h.get("day_of_week")
                open = h.get("opening_time")
                close = h.get("closing_time")
                line = f"{days[day]} : {open} - {close}"
                tmp.append(line)
            hours_of_operation = " ; ".join(tmp) or "<MISSING>"
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
        if i == 3:
            return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
