import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    start_url = "https://gnc.com.mx/tiendas-gnc/"
    domain = "gnc.com.mx"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_codes = DynamicGeoSearch(
        country_codes=[SearchableCountries.MEXICO], expected_search_radius_miles=1
    )
    for lat, lng in all_codes:
        form_key = dom.xpath('//input[@name="form_key"]/@value')[0]
        frm = {
            "search[street]": "",
            "search[radius]": "5",
            "search[measurement]": "km",
            "search[latitude]": lat,
            "search[longitude]": lng,
            "search[tab]": "0",
            "form_key": form_key,
        }
        hdr = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = session.post(start_url, data=frm, headers=hdr)
        dom = etree.HTML(response.text)
        data = dom.xpath('//script[contains(text(), "locationList")]/text()')[-1]
        data = json.loads(data)

        all_locations = data["*"]["Magento_Ui/js/core/app"]["components"][
            "locationList"
        ]["locationItems"]
        for poi in all_locations:
            latitude = poi["latitude"] if poi["latitude"] != "0" else ""
            longitude = poi["longitude"] if poi["longitude"] != "0" else ""
            zip_code = poi["zip"]
            if zip_code and zip_code == "sn":
                zip_code = ""

            item = SgRecord(
                locator_domain=domain,
                page_url="https://gnc.com.mx/tiendas-gnc/",
                location_name=poi["title"],
                street_address=poi["street"],
                city=poi["city"].split(", ")[0],
                state=poi["city"].split(", ")[-1],
                zip_postal=zip_code,
                country_code=poi["country_id"],
                store_number=poi["location_id"],
                phone=poi["phone"],
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="",
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
