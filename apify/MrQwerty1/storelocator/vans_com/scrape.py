import csv
import json

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
    s = set()
    locator_domain = "https://www.vans.com/"
    page_url = "<MISSING>"
    countries = ["US", "DE", "CA"]

    for country in countries:
        data = {
            "request": {
                "appkey": "CFCAC866-ADF8-11E3-AC4F-1340B945EC6E",
                "formdata": {
                    "dataview": "store_default",
                    "geolocs": {
                        "geoloc": [
                            {
                                "addressline": "",
                                "country": f"{country}",
                                "latitude": "",
                                "longitude": "",
                            }
                        ]
                    },
                    "searchradius": "5000",
                    "where": {
                        "country": {"eq": ""},
                        "off": {"eq": "TRUE"},
                        "out": {"eq": ""},
                    },
                },
            }
        }

        r = session.post(
            "https://hosted.where2getit.com/vans/rest/locatorsearch",
            data=json.dumps(data),
        )
        js = r.json()["response"]["collection"]

        for j in js:
            location_name = j.get("name")
            street_address = j.get("address1") or "<MISSING>"
            city = j.get("city") or "<MISSING>"
            postal = j.get("postalcode") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            if country_code == "US":
                state = j.get("state") or "<MISSING>"
            else:
                state = j.get("province") or "<MISSING>"

            store_number = j.get("clientkey")
            if store_number in s:
                continue

            s.add(store_number)
            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            location_type = "<MISSING>"

            _tmp = []
            days = {
                "m": "monday",
                "t": "tuesday",
                "w": "wednesday",
                "thu": "thursday",
                "f": "friday",
                "sa": "saturday",
                "su": "sunday",
            }
            for k, v in days.items():
                time = j.get(k)
                if time:
                    _tmp.append(f"{v}: {time}")

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
