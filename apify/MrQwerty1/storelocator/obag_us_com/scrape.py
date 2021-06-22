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
    locator_domain = "https://www.obag.us.com/"
    api_url = "https://www.obag.us.com/us/storelocator/index/storesbycurrentzoom?ajax=1&lat1=-90&lng1=-180&lat2=90&lng2=180&loadedMarkers=_"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.obag.us.com/us/storelocator/",
        "X-Requested-With": "XMLHttpRequest",
    }
    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()["items"]

    for j in js:
        street_address = j.get("street") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("store_id") or "<MISSING>"
        page_url = j.get("shop_view_url")
        location_name = j.get("title")
        phone = j.get("phone_1") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        hours = j.get("working_times") or []
        d = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": []}

        for h in hours:
            index = h.get("day")
            start = h.get("from")
            end = h.get("to")
            period = f"{start} - {end}"
            d[str(index)].append(period)

        for day, period in zip(days, d.values()):
            _tmp.append(
                f'{day}: {" ".join(period)}'.replace(
                    "00:00 - 00:00 00:00 - 00:00", "Closed"
                ).replace("00:00 00:00 -", "")
            )

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
