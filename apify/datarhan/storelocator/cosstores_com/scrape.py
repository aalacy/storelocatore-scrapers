from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "cosstores.com"
    start_url = "https://www.cosstores.com/en_eur/store-locator.html"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_countries = dom.xpath("//div/@data-countries-with-local-sites")[0][1:-1].split(
        ","
    )
    for country in all_countries:
        data = session.get(
            f"https://api.storelocator.hmgroup.tech/v2/brand/cos/stores/locale/en_GB/country/{country}?openinghours=true&campaigns=true&departments=true"
        ).json()
        all_locations = data["stores"]
        for poi in all_locations:
            hoo = []
            for e in poi["openingHours"]:
                hoo.append(f'{e["name"]} {e["opens"]} - {e["closes"]}')
            hoo = " ".join(hoo)
            state = poi["address"].get("state")
            if not state and poi.get("region"):
                state = poi["region"]["name"]
            city = poi["address"].get("postalAddress")
            if not city:
                city = poi["city"]

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=poi["name"],
                street_address=poi["address"]["streetName1"],
                city=city,
                state=state,
                zip_postal=poi["address"]["postCode"],
                country_code=poi["countryCode"],
                store_number=poi["storeCode"],
                phone=poi["phone"],
                location_type=poi["storeClass"],
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
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
