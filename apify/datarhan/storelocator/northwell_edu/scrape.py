import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "northwell.edu"
    start_url = "https://www.northwell.edu/api/locations/108781?browse_all=true"

    all_poi = []

    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    url = "https://cdns.us1.gigya.com/sdk.config.getAPI?apiKey=3_FTxaSE9O0UuC4sKIHI0TdrJcPmvbKoNumROpQ5uDhkIDSk-4ooTzFaTG6nWd7T2p&pageURL=https%3A%2F%2Fwww.northwell.edu%2Fdoctors-and-care%2Flocations%3Fkeywords%3D%26zip%3DNew%2BYork%252C%2BNew%2BYork%2B10001%26type%3D"
    session.get(url, headers=hdr)
    session.get(
        "https://cdns.us1.gigya.com/sdk.config.getSSO?apiKey=3_e2Uo1FWkcXAk9b3hBYN3Mzuw1w91vVbVG0QNrLKKPZzNRdAh_cDdkilIKEhsHSLK&pageURL=https%3A%2F%2Fwww.northwell.edu",
        headers=hdr,
    )

    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)
    all_poi += data["results"]

    next_page = data["pagination"]["next"]
    while next_page:
        next_page = "https://www.northwell.edu" + next_page
        page_response = session.get(next_page, headers=hdr)
        page_data = json.loads(page_response.text)
        all_poi += page_data["results"]
        if type(page_data["pagination"]) != list:
            next_page = page_data["pagination"].get("next")
        else:
            next_page = None
    for poi in all_poi:
        store_url = poi.get("page_url")
        if store_url:
            if "https" not in store_url:
                store_url = "https:" + store_url
        location_name = poi.get("title")
        street_address = poi.get("street")
        if street_address:
            if poi.get("suite"):
                street_address += ", " + poi["suite"]
        city = poi.get("city")
        state = poi.get("state")
        zip_code = poi.get("zip")
        phone = poi.get("phone")
        geo_data = poi.get("map")
        latitude = ""
        longitude = ""
        if geo_data:
            geo = geo_data.split("center=")[-1].split("&")[0].split(",")
            latitude = geo[0]
            longitude = geo[1]
            if latitude == "-10":
                latitude = ""
                longitude = ""
        store_response = session.get(store_url, headers=hdr)
        store_dom = etree.HTML(store_response.text)
        hours_of_operation = store_dom.xpath(
            '//div[contains(@class, "card__hours")]/table//text()'
        )
        hours_of_operation = " ".join(
            [elem.strip() for elem in hours_of_operation if elem.strip()][2:]
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
