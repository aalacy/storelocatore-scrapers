import re
import csv
import json
from lxml import etree

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.speedyglass.ca/inc/ajax/getSuccursales.cfm"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    formdata = {
        "lang": "en",
        "lieuRechercheLatitude": "",
        "lieuRechercheLongitude": "",
        "lieuRechercheZoom": "",
        "lieuRechercheForm": "",
        "noPage": "13_100",
    }
    response = session.post(start_url, headers=hdr, data=formdata)
    data = json.loads(response.text)

    for poi in data["arrSuccursales"]:
        store_url = poi["urlDetails"]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["succursaleNom"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["adresse1"]
        if poi["adresse2"]:
            street_address += " " + poi["adresse2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["villeNom"]
        city = city if city else "<MISSING>"
        state = poi["provinceNom"]
        state = state if state else "<MISSING>"
        zip_code = poi["codePostal"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "CA"
        store_number = poi["SUCCURSALE_ID"]
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = loc_dom.xpath('//table[@class="tableauHoraire"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            domain,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
