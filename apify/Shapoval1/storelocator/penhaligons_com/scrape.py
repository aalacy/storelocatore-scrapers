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
    locator_domain = "https://www.penhaligons.com/us/en"
    api_url = "https://www.penhaligons.com/us/en/penhaligonsstorelocator/ajax/stores"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.penhaligons.com",
        "Connection": "keep-alive",
        "Referer": "https://www.penhaligons.com/us/en/stores",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }

    data = {
        "latitude": "40.730610",
        "longitude": "-73.935242",
        "radius": "40075000",
        "filter": "",
        "type": "",
    }
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()
    for j in js["stores"]:
        a = j.get("address")
        street_address = f"{a.get('line1')} {a.get('line2')}".strip()
        if street_address.find("25 Kings Road") != -1:
            street_address = street_address.split(",")[0].strip()
        city = a.get("town")
        postal = a.get("postalCode")
        state = "<MISSING>"
        country_code = "".join(a.get("country").get("isocode"))
        if country_code != "GB":
            continue
        store_number = "<MISSING>"
        slug1 = "".join(j.get("code"))
        slug2 = (
            "".join(j.get("displayName")).replace("'", "-").replace(" ", "-").lower()
        )
        page_url = f"https://www.penhaligons.com/us/en/stores/{slug2}/{slug1}"
        if page_url.find("burlington-arcade") != -1:
            continue
        if page_url.find("canary-wharf") != -1:
            street_address = street_address + " " + "Canary Wharf"
        location_name = j.get("displayName")
        phone = a.get("phone") or "<MISSING>"
        latitude = j.get("geoPoint").get("latitude")
        longitude = j.get("geoPoint").get("longitude")
        location_type = "".join(j.get("puigStoreType")).strip()
        if location_type != "Store":
            continue
        status = j.get("status")
        hours = j.get("openingHours").get("weekDayOpeningList")[1:]
        tmp = []
        for h in hours:
            day = "".join(h["weekDay"])
            closed = "Closed"
            try:
                open = "".join(h.get("openingTime").get("formattedHour"))
                close = "".join(h.get("closingTime").get("formattedHour"))
                line = f"{day} : {open} - {close}"
                tmp.append(line)
            except AttributeError:
                line = f"{day} : {closed}"
                tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"
        if status == "TEMPORARILY_CLOSED":
            hours_of_operation = "TEMPORARILY CLOSED".lower()

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
