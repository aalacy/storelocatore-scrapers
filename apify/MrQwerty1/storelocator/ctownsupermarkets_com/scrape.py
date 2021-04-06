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
    locator_domain = "https://ctownsupermarkets.com/"

    session = SgRequests()
    for i in range(0, 100000, 50):
        r = session.get(
            f"https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=2500&location=40291"
            f"&limit=50&api_key=62850d78675a712e91b03d1d5868d470&v=20181201&offset={i}&savedFilterIds=29721495"
        )
        js = r.json()["response"]["entities"]

        for j in js:

            a = j.get("address")
            street_address = f"{a.get('line1')}".strip() or "<MISSING>"
            city = a.get("city") or "<MISSING>"
            location_name = f"{j.get('name')} {city}"
            page_url = j.get("landingPageUrl") or "<MISSING>"

            if location_name.lower().find(" open") != -1:
                location_name = j.get("name")

            state = a.get("region") or "<MISSING>"
            postal = a.get("postalCode") or "<MISSING>"
            country_code = a.get("countryCode") or "<MISSING>"
            store_number = "<MISSING>"
            phone = j.get("mainPhone") or "<MISSING>"
            latitude = j.get("yextDisplayCoordinate", {}).get("latitude") or "<MISSING>"
            longitude = (
                j.get("yextDisplayCoordinate", {}).get("longitude") or "<MISSING>"
            )
            location_type = "<MISSING>"

            hours = j.get("hours") or {}
            _tmp = []
            for k, v in hours.items():
                if k == "holidayHours":
                    continue

                day = k
                isclosed = v.get("isClosed")
                if not isclosed:
                    interval = v.get("openIntervals")[0]
                    start = interval.get("start")
                    end = interval.get("end")
                    line = f"{day.capitalize()}: {start} - {end}"
                    _tmp.append(line)
                else:
                    _tmp.append("Closed")
                    break

            hours_of_operation = ";".join(_tmp) or "<MISSING>"

            if (
                hours_of_operation.count("Closed") == 7
                or location_name.lower().find("closed") != -1
            ):
                hours_of_operation = "Closed"

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
        if len(js) < 50:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
