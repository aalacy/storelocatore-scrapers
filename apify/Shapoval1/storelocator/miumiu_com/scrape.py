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

    locator_domain = "https://www.miumiu.com/"
    api_url = (
        "https://www.miumiu.com/us/en/store-locator.miumiu.getAllStoresByBrand.json"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["allStores"]
    for j in js.values():
        country_code = j.get("country")
        if country_code != "US":
            continue
        slug = "".join(j.get("storeName"))
        page_url = f"https://www.miumiu.com/us/en/store-detail.{slug}.html"
        location_name = j.get("Description")[0].get("displayStoreName")
        location_type = "<MISSING>"
        street_address = "".join(j.get("addressLine")[0]).replace(
            "9700 Collins Avenue,", "9700 Collins Avenue"
        )
        street_address = street_address.split(",")[0].replace("NY", "")
        phone = j.get("telephone1")
        state = j.get("stateOrProvinceName")
        postal = j.get("postalCode")
        city = j.get("city")
        store_number = "<MISSING>"
        days = [
            "sunday",
            "saturday",
            "tuesday",
            "friday",
            "wednesday",
            "thursday",
            "monday",
        ]
        tmp = []
        for d in days:
            days = d
            times = j.get("Attribute").get("WH_DAY").get(f"{d}")
            line = f"{days} {times}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp)
        latitude = j.get("latitude")
        longitude = j.get("longitude")

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
