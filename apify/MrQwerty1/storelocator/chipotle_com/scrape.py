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
    locator_domain = "https://chipotle.com/"
    api_url = "https://services.chipotle.com/restaurant/v3/restaurant"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": "b4d9f36380184a3788857063bce25d6a",
    }

    data = '{"latitude":33.0218117,"longitude":-97.12516989999997,"radius":20000000,"restaurantStatuses":["OPEN","LAB"],"orderBy":"distance","orderByDescending":false,"pageSize":4000,"pageIndex":0,"embeds":{"addressTypes":["MAIN"],"publicPhoneTypes":["MAIN PHONE"],"normalHours":true}}'

    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["data"]

    for j in js:
        a = j.get("addresses")[0]
        street_address = a.get("addressLine1") or "<MISSING>"
        city = a.get("locality") or "<MISSING>"
        state = a.get("administrativeArea") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("countryCode") or "<MISSING>"
        store_number = j.get("restaurantNumber") or "<MISSING>"
        page_url = "<MISSING>"
        location_name = j.get("restaurantName")
        try:
            phone = j["publicPhones"][0]["phoneNumber"]
        except:
            phone = "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        location_type = j.get("restaurantLocationType") or "<MISSING>"

        _tmp = []
        hours = j.get("normalHours") or []
        for h in hours:
            day = h.get("dayOfWeek")
            if not day:
                continue
            start = h.get("openTime")
            end = h.get("closeTime")
            _tmp.append(f"{day}: {start} - {end}")

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
    session = SgRequests()
    scrape()
