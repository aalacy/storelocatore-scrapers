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
    locator_domain = "https://geodis.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.post(
        "https://geodis.com/geodis_custom_ajax_get_all_locations", headers=headers
    )
    js = r.json()
    s = set()
    for j in js:
        node_id = j.get("node_id")
        latitude = j.get("coordinates")[0]
        longitude = j.get("coordinates")[1]

        session = SgRequests()
        data = {"node_id": f"{node_id}"}
        r = session.post(
            "https://geodis.com/geodis_custom_ajax_get_agency_popup",
            headers=headers,
            data=data,
        )
        tree = html.fromstring(r.text)
        page_url = "https://geodis.com/locations"
        street_address = (
            " ".join(tree.xpath('//span[@class="address-line1"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        city = (
            " ".join(tree.xpath('//span[@class="locality"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        state = (
            " ".join(tree.xpath('//span[@class="administrative-area"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )

        postal = (
            " ".join(tree.xpath('//span[@class="postal-code"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if postal.find("Buenos Aires") != -1:
            postal = "<MISSING>"
        if postal.find("Co. Dublin") != -1:
            postal = postal.replace("Co. Dublin", "").strip()
        postal = (
            postal.replace("French Guiana", "")
            .replace("DOM TOM", "")
            .replace("Metro Manila", "")
            .replace("Taipei City", "")
            .replace("Songkhla", "")
            .replace("Chon Buri", "")
            .replace("Bangkok", "")
            .replace("NY-", "")
            .strip()
        )
        if postal.find("Santiago") != -1:
            postal = "<MISSING>"

        location_name = (
            " ".join(tree.xpath('//div[@class="title-agency-view"]/a/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )

        country_code = (
            " ".join(tree.xpath('//span[@class="country"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if postal.find(" ") != -1 and country_code == "United States":
            po = postal
            state = po.split()[0].strip()
            postal = po.split()[1].strip()
        if postal.find("Province") != -1 and country_code == "China":
            po = postal
            state = " ".join(po.split()[:-1])
            postal = po.split()[-1].strip()
        store_number = node_id
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath('//div[1][@class="group-clock-view"]/div/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if (
            hours_of_operation.count("24/7") == 7
            or hours_of_operation.count("24/7") > 7
        ):
            hours_of_operation = "24/7"
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        if phone.find("|") != -1:
            phone = phone.split("|")[0].strip()
        if phone.find("(Wittelsheim)") != -1:
            phone = phone.split("(Wittelsheim)")[1].strip()
        if phone == "0" or phone == "2":
            phone = "<MISSING>"

        line = street_address
        if line in s:
            continue
        s.add(line)

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
