import csv
from sgrequests import SgRequests
from datetime import datetime


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
    locator_domain = "https://www.swisschalet.com/en"
    api_url = "https://iosapi.swisschalet.com/CaraAPI/APIService/getStoreList?from=60.000,-150.000&to=39.000,-50.000&eCommOnly=N"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Origin": "https://www.swisschalet.com",
        "Proxy-Authorization": "Basic VEYwYmJlZGNkNWM1YmE1YWZjNDhhOTQ4MjcxMDlmMGJhMS5oNzgzb2hhdzA5amRmMDpURjBiYmVkY2Q1YzViYTVhZmM0OGE5NDgyNzEwOWYwYmExLmg3ODIzOWhk",
        "Connection": "keep-alive",
        "Referer": "https://www.swisschalet.com/en/locations.html",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js["response"]["responseContent"]["storeModel"]:

        street_address = f"{j.get('streetNumber')} {j.get('street')}"
        street = "".join(j.get("street")).replace(" ", "-")
        city = j.get("city") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        phone = "".join(j.get("phoneNumber")) or "<MISSING>"
        if phone.find("X") != -1:
            phone = phone.split("X")[0].strip()
        country_code = "CA"
        store_number = j.get("storeNumber")
        location_name = j.get("storeName") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        page_url = f"https://www.swisschalet.com/en/locations/{store_number}/{city}-{street}.html"
        api_url = f"https://iosapi.swisschalet.com/CaraAPI/APIService/getStoreDetails?storeNumber={store_number}&numberOfStoreHours=7"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Origin": "https://www.swisschalet.com",
            "Proxy-Authorization": "Basic VEYwYmJlZGNkNWM1YmE1YWZjNDhhOTQ4MjcxMDlmMGJhMS5oNzgzb2hhdzA5amRmMDpURjBiYmVkY2Q1YzViYTVhZmM0OGE5NDgyNzEwOWYwYmExLmg3ODIzOWhk",
            "Connection": "keep-alive",
            "Referer": "https://www.swisschalet.com/en/locations.html",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
        r = session.get(api_url, headers=headers)
        js = r.json()["response"]["responseContent"]
        tmp = []
        for k in js["hours"]:

            open = k.get("store").get("open")
            close = k.get("store").get("close")
            date = k.get("date")
            t = datetime.strptime(date, "%Y-%m-%d")
            day = t.strftime("%A")
            line = f"{day} : {open} - {close}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"

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
