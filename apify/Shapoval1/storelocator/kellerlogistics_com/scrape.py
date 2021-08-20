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

    locator_domain = "https://kellerlogistics.com"
    api_url = "https://www.google.com/maps/d/embed?mid=1AiYcgzVuftfkcloKe7ggeZehgfI&ll=37.80993328494997%2C-103.36728791599614&z=5"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    cleaned = (
        r.text.replace("\\t", " ")
        .replace("\t", " ")
        .replace("\\n]", "]")
        .replace("\n]", "]")
        .replace("\\n,", ",")
        .replace("\\n", "#")
        .replace('\\"', '"')
        .replace("\\u003d", "=")
        .replace("\\u0026", "&")
        .replace("\\", "")
        .replace("\xa0", " ")
    )

    locations = json.loads(
        cleaned.split('var _pageData = "')[1].split('";</script>')[0]
    )[1][6][0][12][0][13][0]
    for l in locations:

        page_url = "https://kellerlogistics.com/warehousing/facilities/"
        location_name = l[5][0][1][0]
        location_type = "<MISSING>"
        street_address = "".join(l[5][3][0][1])
        state = "".join(l[5][3][2][1])
        postal = "".join(l[5][3][3][1])
        country_code = "US"
        city = "".join(l[5][3][1][1])
        store_number = "<MISSING>"
        latitude = l[1][0][0][0]
        longitude = l[1][0][0][1]
        try:
            phone = "".join(l[5][3][4][1])
        except:
            phone = "<MISSING>"
        if phone.find(",") != -1:
            phone = phone.split(",")[0].strip()

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
