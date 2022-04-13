import json
from bs4 import BeautifulSoup
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36"
    }
    session = SgRequests(verify_ssl=False)
    r = session.get("https://www.extendedstayamerica.com/hotels", headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    jd = (
        str(soup)
        .split("window.esa.hotelsData = ")[1]
        .split("</script>")[0]
        .replace("}];", "}]")
    )

    json_data = json.loads(jd)

    for value in json_data:

        a = value["address"]

        location_name = value["title"]
        street_address = a["street"]
        city = a["city"]
        state = a["region"]
        zipp = a["postalCode"]
        country_code = "US"
        store_number = value["siteId"]

        location_type = "<MISSING>"
        latitude = value["latitude"]
        longitude = value["longitude"]
        hours_of_operation = "Open 24 hours a day, seven days a week"
        page_url = "https://www.extendedstayamerica.com" + value["urlMap"]
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        js_block = "".join(
            tree.xpath('//script[contains(text(), "streetAddress")]/text()')
        )
        try:
            phone = js_block.split('"telephone": "')[1].split('"')[0].strip()
        except:
            phone = "<MISSING>"

        item = SgRecord(
            locator_domain="extendedstayamerica.com",
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
