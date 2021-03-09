import csv
from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address


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
    locator_domain = "https://www.balenciaga.com/"

    session = SgRequests()

    countries = ["US", "CA"]

    for country in countries:
        api_url = f"https://www.balenciaga.com/on/demandware.store/Sites-BAL-INTL-Site/en_ZW/Stores-FindStoresData?countryCode={country}"
        r = session.get(api_url)
        js = r.json()["storesData"]["stores"]

        for j in js:
            line = (
                f"{j.get('address1')} {j.get('address2') or ''}".replace(
                    "\n", ", "
                ).strip()
                or "<MISSING>"
            )

            city = j.get("city") or "<MISSING>"
            state = j.get("stateCode") or "<MISSING>"
            postal = j.get("postalCode") or "<MISSING>"

            adr = parse_address(International_Parser(), line, postcode=postal, city=city, state=state)

            street_address = (
                    f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                        "None", ""
                    ).strip()
                    or "<MISSING>"
            )
            city = adr.city or "<MISSING>"
            state = adr.state or "<MISSING>"
            postal = adr.postcode or "<MISSING>"
            country_code = j.get("countryCode") or "<MISSING>"
            store_number = j.get("ID") or "<MISSING>"
            page_url = j.get("detailsUrl") or "<MISSING>"
            location_name = j.get("storeName")
            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            location_type = "<MISSING>"

            _tmp = []
            days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            for d in days:
                part = d[:3].lower()
                time = j.get(f"{part}Hours")
                if time.lower().find("no data") != -1:
                    continue
                _tmp.append(f"{d}: {time}")

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
    scrape()
