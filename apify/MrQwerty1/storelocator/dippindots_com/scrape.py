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
    url = "https://www.dippindots.com/"

    session = SgRequests()

    for i in range(1, 10000):
        api_url = f"https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=QFUTTCVJJITGJYAE&pageSize=100&page={i}"
        r = session.get(api_url)
        js = r.json()

        for j in js:
            page_url = (
                "https://www.dippindots.com/loc" + j.get("llp_url") or "<MISSING>"
            )
            location_type = j.get("open_or_closed").capitalize() or "<MISSING>"

            j = j["store_info"]
            locator_domain = url
            street_address = (
                f"{j.get('address')} {j.get('address_extended') or ''}" or "<MISSING>"
            )
            city = j.get("locality") or "<MISSING>"
            location_name = f"{j.get('name')} {city}"
            state = j.get("region") or "<MISSING>"
            postal = j.get("postcode") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            if country_code != "US":
                continue
            store_number = "<MISSING>"
            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            hours = j.get("store_hours") or "<MISSING>"

            if hours == "<MISSING>":
                hours_of_operation = hours
            else:
                _tmp = []
                days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                hours = hours.split(";")[:-1]
                i = 0
                for d in days:
                    try:
                        time = hours[i].split(",")
                    except IndexError:
                        i += 1
                        _tmp.append(f"{d}: Closed")
                        continue
                    start = f"{time[1][:2]}:{time[1][2:]}"
                    close = f"{time[2][:2]}:{time[2][2:]}"
                    _tmp.append(f"{d}: {start} - {close}")
                    i += 1

                hours_of_operation = ";".join(_tmp)

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
        if len(js) < 100:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
