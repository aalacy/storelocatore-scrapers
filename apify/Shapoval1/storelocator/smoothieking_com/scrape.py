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

    locator_domain = "https://www.smoothieking.com/"
    for i in range(1, 12, 1):
        api_url = f"https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=TLLLFMCOPXOWXFMY&center=38.541749,-98.428791&coordinates=14.000736333338665,-57.91121287500016,56.89252313204278,-138.94636912499985&multi_account=false&page={i}&pageSize=100"

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        js = r.json()

        for j in js:

            a = j.get("store_info")
            page_url = "".join(a.get("website"))
            if (
                page_url.find("https://www.smoothieking.com/international/trinidad")
                != -1
            ):
                continue

            location_name = a.get("name")
            status = "".join(j.get("status"))
            location_type = "<MISSING>"
            if status != "open":
                location_type = status
            street_address = f"{a.get('address')} {a.get('address_extended')}".replace(
                "None", ""
            ).strip()
            phone = a.get("phone") or "<MISSING>"
            state = a.get("region")
            postal = "".join(a.get("postcode"))
            if postal.find("KY1-1106") != -1:
                continue
            country_code = a.get("country")
            city = a.get("locality")
            store_number = "<MISSING>"
            latitude = a.get("latitude")
            longitude = a.get("longitude")
            hours_of_operation = (
                "".join(a.get("hours"))
                .replace("1,", "Monday ")
                .replace("2,", "Tuesday ")
                .replace("3,", "Wednesday ")
                .replace("4,", "Thursday ")
                .replace("5,", "Friday ")
                .replace("6,", "Saturday ")
                .replace("7,", "Sunday ")
                .replace("000", "0.00")
                .replace("00", ".00")
                .replace("30", ".30")
                .replace("..", ".")
                or "<MISSING>"
            )

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
