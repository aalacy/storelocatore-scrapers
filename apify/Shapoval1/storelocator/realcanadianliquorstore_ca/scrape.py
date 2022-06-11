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
    locator_domain = "https://www.realcanadianliquorstore.ca"
    api_url = "https://ws2.bullseyelocations.com/RestSearch.svc/DoSearch2?ClientId=4664&ApiKey=27ab1bab-2901-4156-aec2-bfb51a7ce538&CountryId=3&CountryScope=ALL&FillAttr=true&GetHoursForUpcomingWeek=true&LanguageCode=en&Latitude=53.5461245&Longitude=-113.4938229&Radius=20000&SearchTypeOverride=1&MaxResults=50&PageSize=50&StartIndex=0&CategoryIDs=93194&MatchAllCategories=true"
    session = SgRequests()

    r = session.get(api_url)
    js = r.json()
    for j in js["ResultList"]:
        slug = j.get("ThirdPartyId")
        street_address = j.get("Address1")
        city = j.get("City")
        postal = j.get("PostCode")
        state = j.get("State")
        country_code = j.get("CountryName")
        store_number = "<MISSING>"
        page_url = (
            f"https://www.realcanadianliquorstore.ca/find-location/?location={slug}"
        )
        phone = j.get("PhoneNumber")
        location_name = j.get("Name")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        location_type = "<MISSING>"
        hours_of_operation = j.get("BusinessHours")

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
