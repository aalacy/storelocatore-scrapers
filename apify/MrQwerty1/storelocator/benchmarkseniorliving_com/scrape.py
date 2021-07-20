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
    locator_domain = "https://www.benchmarkseniorliving.com/"
    api_url = "https://www.benchmarkseniorliving.com/graphql"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.benchmarkseniorliving.com/our-communities",
        "content-type": "application/json",
        "Origin": "https://www.benchmarkseniorliving.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }

    data = '{"operationName":null,"variables":{},"query":"{\\n nodes: nodeQuery(\\n limit: 1000\\n filter: {conditions: [{field: \\"type\\", value: \\"community\\"}, {field: \\"status\\", value: \\"1\\"}]}\\n ) {\\n entities {\\n title: entityLabel\\n id: entityId\\n url: entityUrl {\\n path\\n __typename\\n }\\n ... on NodeCommunity {\\n externalLink: fieldExternalLink {\\n url {\\n path\\n __typename\\n }\\n __typename\\n }\\n address: fieldAddress {\\n addressLine1\\n addressLine2\\n locality\\n administrativeArea\\n postalCode\\n __typename\\n }\\n description: fieldTeaserDescription {\\n processed\\n __typename\\n }\\n fieldAverageRating\\n fieldGallery {\\n entity {\\n ... on MediaImage {\\n fieldMediaImage {\\n derivative(style: SMALL) {\\n url\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n fieldCareTypes {\\n entity {\\n entityLabel\\n __typename\\n }\\n __typename\\n }\\n position: fieldGeoLocation {\\n lat\\n lng: lon\\n __typename\\n }\\n phone: fieldPhoneNumber\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n}\\n"}'

    session = SgRequests()
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["data"]["nodes"]["entities"]

    for j in js:
        a = j.get("address")
        street_address = (
            f"{a.get('addressLine1')} {a.get('addressLine2') or ''}".strip()
            or "<MISSING>"
        )
        city = a.get("locality") or "<MISSING>"
        state = a.get("administrativeArea") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        slug = j["url"]["path"]
        page_url = f"https://www.benchmarkseniorliving.com{slug}"
        location_name = j.get("title")
        phone = j.get("phone") or "<MISSING>"
        loc = j.get("position") or {}
        latitude = loc.get("lat") or "<MISSING>"
        longitude = loc.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
