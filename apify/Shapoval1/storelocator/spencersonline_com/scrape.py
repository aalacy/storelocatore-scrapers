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
    locator_domain = "hhttps://www.spencersonline.com"
    api_url = "https://www.spencersonline.com/custserv/locate_store.cmd"
    session = SgRequests()
    r = session.post(api_url)

    for i in range(1, 829):
        store_number = (
            r.text.split("store.STORE_NUMBER = '")[i]
            .split("store.ADDRESS_LINE_1")[0]
            .replace("';", "")
            .strip()
            .lstrip()
        )
        street_address = (
            r.text.split("store.ADDRESS_LINE_2 = '")[i]
            .split("store.CITY = '")[0]
            .replace("';", "")
            .replace("&#45;", "-")
            .strip()
        ) or "<MISSING>"
        if street_address == "X":
            continue
        latitude = (
            r.text.split("store.LATITUDE = '")[i]
            .split("store.LONGITUDE = '")[0]
            .replace("';", "")
            .strip()
        )
        longitude = (
            r.text.split("store.LONGITUDE = '")[i]
            .split("store.STORE_STATUS = '")[0]
            .replace("';", "")
            .strip()
        )
        postal = (
            r.text.split("store.ZIP_CODE = '")[i]
            .split("store.PHONE = '")[0]
            .replace("';", "")
            .strip()
        )
        phone = (
            r.text.split("store.PHONE = '")[i]
            .split("store.LATITUDE = '")[0]
            .replace("';", "")
            .strip()
        )
        country_code = (
            r.text.split("store.COUNTRY_CODE ='")[i]
            .split("store.ZIP_CODE = '")[0]
            .replace("';", "")
            .strip()
        )
        state = (
            r.text.split("store.STATE ='")[i]
            .split("store.COUNTRY_CODE =")[0]
            .replace("';", "")
            .strip()
        )
        city = (
            r.text.split("store.CITY = '")[i]
            .split("store.STATE ='")[0]
            .replace("';", "")
            .strip()
        )
        location_name = (
            r.text.split("store.STORE_NAME = '")[i]
            .split("store.STORE_NUMBER = '")[0]
            .replace("';", "")
            .strip()
        )
        hours_of_operation = (
            r.text.split("store.STORE_STATUS = '")[i]
            .split("';")[0]
            .strip()
            .replace("Coming Soon", "<MISSING>")
        )
        STORE_ID = (
            r.text.split("store.STORE_ID = '")[i]
            .split("store.STORE_NAME = '")[0]
            .replace("';", "")
            .strip()
        )
        page_url = (
            "https://www.spencersonline.com/store/"
            + str(location_name.strip().lstrip().replace(" ", "-"))
            + "/"
            + str(STORE_ID.strip().lstrip())
            + ".uts"
        )
        location_type = "<MISSING>"
        if hours_of_operation.find("Closed") != -1:
            hours_of_operation = "Closed"
        else:
            hours_of_operation = "<MISSING>"
        if latitude == "0" or longitude == "0":
            longitude = "<MISSING>"
            latitude = "<MISSING>"
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
