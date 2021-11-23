import csv
from lxml import html
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

    locator_domain = "https://keyes.com/"
    api_url = "https://offices.keyes.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "defaultListData ")]/text()'))
        .split("$config.defaultListData = '")[1]
        .split("';")[0]
        .replace("\\", "")
    )
    jsblock = jsblock.replace(
        '"hours_sets:primary":"', '"hours_sets:primary":\''
    ).replace('","more_info_button"', '\',"more_info_button"')

    js = eval(jsblock)

    for j in js:

        page_url = j.get("url")
        if page_url == "https://offices.keyes.com/fl/miami/keyes-offices-v001.html":
            continue
        location_name = j.get("location_name")
        location_type = "Keyes Office"
        street_address = f"{j.get('address_1')} {j.get('address_2') or ''}".replace(
            ", Seabranch Square Plaza", ""
        ).strip()
        phone = j.get("local_phone")
        state = j.get("region")
        postal = j.get("post_code")
        country_code = j.get("country")
        city = j.get("city")
        store_number = j.get("fid")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = (
            "".join(j.get("hours_sets:primary"))
            .split('"days":')[1]
            .split(',"timezone"')[0]
            .replace('"', "")
            .replace("{", "")
            .replace("}", "")
            .replace("[", "")
            .replace("]", "")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.replace("open:", "")
            .replace(",close:", " - ")
            .replace("day:", "day ")
        )

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
