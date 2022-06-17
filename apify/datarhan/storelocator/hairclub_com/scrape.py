from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries, DynamicZipSearch


def fetch_data():
    session = SgRequests()
    domain = "hairclub.com"
    start_url = "https://leads-api-prod.hairclub.com/api/Center/cards?ZipCode={}"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        expected_search_radius_miles=100,
    )
    for code in all_codes:
        hdr = {
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2NvcmVzZXJ2aWNlcy1hcGktcHJvZC5henVyZXdlYnNpdGVzLm5ldC8iLCJpYXQiOm51bGwsImV4cCI6bnVsbCwiYXVkIjoiaHR0cHM6Ly9jb3Jlc2VydmljZXMtYXBpLXByb2QuYXp1cmV3ZWJzaXRlcy5uZXQvIiwic3ViIjoiIn0.sFasu1GnH1rdp48mj-wjMuBlZCswQp-UBXXWvhxyUtA"
        }
        all_locations = session.get(start_url.format(code), headers=hdr)
        if not all_locations.text.strip():
            all_codes.found_nothing()
            continue
        for poi in all_locations.json():
            hoo = []
            for e in poi["availability"]:
                if poi.get("openingHour"):
                    hoo.append(
                        f'{e["day"]}: {poi["openingHour"]} - {poi["closingHour"]}'
                    )
                else:
                    hoo.append(f'{e["day"]}: closed')
            hoo = " ".join(hoo)
            page_url = (
                f'https://www.hairclub.com/locations/hair-loss-clinic-{poi["idCenter"]}'
            )
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            zip_code = loc_dom.xpath('//div[@class="address-line-2"]/p/text()')
            if not zip_code:
                zip_code = loc_dom.xpath('//div[@class="hours-block"]/p[1]/text()')
            zip_code = zip_code[0].split()[-1]
            all_codes.found_location_at(
                poi["position"]["latitude"], poi["position"]["longitude"]
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=poi["address"],
                city=poi["city"],
                state=poi["state"],
                zip_postal=zip_code,
                country_code=poi["country"],
                store_number=poi["idCenter"],
                phone=poi["phone"],
                location_type=SgRecord.MISSING,
                latitude=poi["position"]["latitude"],
                longitude=poi["position"]["longitude"],
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
