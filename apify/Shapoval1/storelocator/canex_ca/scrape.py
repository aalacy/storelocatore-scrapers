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

    locator_domain = "https://www.canex.ca"
    s = set()
    for i in range(0, 50, 10):
        api_url = f"https://www.canex.ca/en/store/locator/ajaxlist/?loaded={i}&latitude=49.5892&longitude=34.5537&_=1625922885068"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Referer": "https://www.canex.ca/en/store",
            "TE": "Trailers",
        }
        r = session.get(api_url, headers=headers)
        js = r.json()["list"]

        for j in js:

            page_url = j.get("additional_attributes").get("url_key")
            location_name = j.get("name")
            location_type = "<MISSING>"
            street_address = " ".join(j.get("address"))
            phone = "".join(j.get("telephone")) or "<MISSING>"
            if phone.find(" ") != -1:
                phone = phone.split()[0].strip()
            state = j.get("region")
            postal = j.get("postcode")
            if postal == " Alberta":
                postal = "<MISSING>"
            country_code = "CA"
            city = j.get("city")
            store_number = "<MISSING>"
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            hours = j.get("opening_hours")
            hours = eval(hours)
            tmp = []
            for h in hours:
                day = h.get("dayLabel")
                opens = h.get("open_formatted")
                closes = h.get("close_formatted")
                line = f"{day} {opens} - {closes}"
                if opens == closes:
                    line = f"{day} - Closed"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp) or "<MISSING>"
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "Closed"

            line = street_address
            if line in s:
                continue
            s.add(line)

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
