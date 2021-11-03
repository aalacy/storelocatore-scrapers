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

    locator_domain = "https://www.instacheques.ca/"
    api_url = "https://www.instacheques.ca/storeLocatorService/stores/all/cities"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        slug1 = "".join(j.get("city"))
        if slug1 == "St. Laurent":
            slug1 = "St%20Laurent"
        slug2 = "".join(j.get("province"))
        if slug2 != "QC":
            continue

        api_url1 = f"https://www.instacheques.ca/storeLocatorService/stores/{slug2}/cities?cityName={slug1}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url1, headers=headers)
        js = r.json()
        for j in js:
            location_name = "".join(j.get("businessName"))

            street_address = (
                f"{j.get('streetAddress1')} {j.get('streetAddress2')}".replace(
                    "None", ""
                ).strip()
            )
            state = j.get("stateProvinceId") or "<MISSING>"
            postal = j.get("postCode") or "<MISSING>"
            city = j.get("cityTown") or "<MISSING>"
            country_code = j.get("countryId")
            location_type = "<MISSING>"
            store_number = j.get("storeNumber")
            phone = j.get("phone")
            latitude = j.get("latitudeCoordinate")
            longitude = j.get("longitudeCoordinate")
            citySlug = "".join(city)
            streetSlug = "".join(street_address).replace(" ", "-")
            if citySlug.find("Greenfield Park") != -1:
                citySlug = "Greenfield-Park"
            page_url = f"https://www.instacheques.ca/en/store-locator/findastore/Quebec/{citySlug}"
            if (
                page_url
                == "https://www.instacheques.ca/en/store-locator/findastore/Quebec/Montreal"
                or page_url
                == "https://www.instacheques.ca/en/store-locator/findastore/Quebec/Laval"
            ):
                page_url = f"https://www.instacheques.ca/en/store-locator/StoreDetails?CA/QC/{city}/{streetSlug}/{postal}/{store_number}"
            hours_of_operation = j.get("hrsAbbr")

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
