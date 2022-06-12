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

    locator_domain = "https://www.flipflopshops.com"
    api_url = "https://flipflopshops.locally.com/stores/conversion_data?has_data=true&company_id=14484&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=32.51594939854979&map_center_lng=34.54069999999943&map_distance_diag=8078.261302286804&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=2"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["markers"]:
        slug = "".join(j.get("city")).replace(" ", "").lower()
        page_url = f"https://flipflopshops{slug}.locally.com/"
        location_name = j.get("name")
        location_type = "<MISSING>"
        street_address = j.get("address")
        phone = j.get("phone") or "<MISSING>"
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        if country_code != "CA" and country_code != "US":
            continue
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours = j.get("display_dow")
        tmp = []
        for h in hours.values():
            day = h.get("label")
            time = h.get("bil_hrs")
            line = f"{day} - {time}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"
        if hours_of_operation.count("Closed") == 7:
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

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
