from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "nautica.com"
    start_url = "https://www.nautica.com/stores"

    url = "https://www.nautica.com/on/demandware.store/Sites-nau-Site/default/Stores-GetNearestStores?countryCode={}&onlyCountry=true"
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_countries = dom.xpath(
        '//select[@id="dwfrm_storelocator_country"]/option/@value'
    )
    for code in all_countries:
        all_locations = session.get(url.format(code)).json()
        for poi in all_locations.values():
            page_url = f"https://www.nautica.com/stores?storeid={poi['storeID']}"
            hoo = ""
            if poi["storeHours"]:
                hoo = etree.HTML(poi["storeHours"]).xpath("//text()")
            if hoo:
                hoo = " ".join(" ".join(hoo).split())

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=poi["address1"],
                city=poi["city"],
                state=poi["stateCode"],
                zip_postal=poi["postalCode"],
                country_code=poi["countryCode"],
                store_number=poi["storeID"],
                phone=poi["phone"],
                location_type=poi["department"],
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
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
