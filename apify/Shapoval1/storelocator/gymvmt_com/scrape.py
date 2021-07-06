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

    locator_domain = "https://gymvmt.com/"
    api_url = "https://gymvmt.com/clubs/"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var allLocations = ")]/text()'))
        .split("var allLocations = ")[1]
        .split(";")[0]
    )
    jsblock = (
        jsblock.replace("name", '"name"')
        .replace("lat", '"lat"')
        .replace("lng", '"lng"')
        .replace("address", '"address"')
        .replace("city", '"city"')
    )
    jsblock = (
        jsblock.replace("province", '"province"')
        .replace("zip", '"zip"')
        .replace("directions", '"directions"')
        .replace("phone", '"phone"')
        .replace("hours", '"hours"')
    )
    jsblock = (
        jsblock.replace("schedule", '"schedule"')
        .replace("club", '"club"')
        .replace("filters", '"filters"')
        .replace("id", '"id"')
        .replace('/"club"s/', "/'club's/")
        .replace('"city"', "'city'")
    )
    jsblock = (
        jsblock.replace('k"id"s-"club"', "k'id's-'club'")
        .replace('tru-r"id"e-studio', "tru-r'id'e-studio")
        .replace('M"id"park', "M'id'park")
        .replace('m"id"napore/', "m'id'napore/")
        .replace('Hol"id"ays', "Holidays")
        .replace('"club"', "'club'")
    )
    jsblock = jsblock.replace("{", "[").replace("}", "]").replace(":", "")
    js = eval(jsblock)

    for j in js:
        slug = "".join(j[11]).split("club/")[1]
        slug = "".join(slug).replace("'", "")
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(j[0]).split("name")[1].strip()
        location_type = "gym"
        street_address = "".join(j[3]).split("address")[1].replace("'", "").strip()
        tmpcls = "".join(j[3]).split("address")[1].strip()
        street_address = (
            street_address.replace("<strong>Permanently Closed</strong>", "")
            .replace("<strong>Temporarily Closed</strong>", "")
            .replace("</br>", "")
            .strip()
        )
        phone = "".join(j[8]).split("phone")[1].strip()
        state = "".join(j[5]).split("province")[1].strip()
        postal = "".join(j[6]).split("zip")[1].strip()
        country_code = "CA"
        city = "".join(j[4]).split("city")[1].strip()
        store_number = "<MISSING>"
        latitude = "".join(j[1]).split("lat")[1].strip()
        longitude = "".join(j[2]).split("lng")[1].strip()

        hours_of_operation = (
            "".join(j[9:]).split("hours")[1].split("Holidays")[0].strip()
        )
        if "Permanently Closed" in tmpcls:
            hours_of_operation = "Permanently Closed"
        if "Temporarily Closed" in tmpcls:
            hours_of_operation = "Temporarily Closed"
        if (
            hours_of_operation.find("<strong>") != -1
            and page_url.find("edgemont") == -1
        ):
            hours_of_operation = (
                " ".join(hours_of_operation.split("<strong>")[1:])
                .replace("</strong>", "")
                .replace("</br>", "")
            )
        hours_of_operation = (
            hours_of_operation.replace("</strong>", "")
            .replace("</br>", "")
            .replace("<strong>", "")
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
