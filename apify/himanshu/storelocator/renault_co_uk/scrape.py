# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://dealerlocator.renault.co.uk/data/GetDealersList"
    domain = "renault.co.uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded",
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=20
    )
    for code in all_codes:
        frm = {"postcode": code}
        data = session.post(start_url, headers=hdr, data=frm).json()
        for poi in data["Result"]["Dealers"]:
            street_address = poi["AddressLine1"]
            if poi["AddressLine2"]:
                street_address += ", " + poi["AddressLine2"]
            hoo = []
            hoo_data = poi["OpeningHours"]
            if hoo_data:
                for e in hoo_data:
                    hoo.append(f'{e["Label"]}: {e["Value"]}')
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://dealerlocator.renault.co.uk/",
                location_name=poi["DealerName"],
                street_address=street_address,
                city=poi["Town"],
                state=poi["County"],
                zip_postal=poi["PostCode"],
                country_code="",
                store_number=poi["DealerId"],
                phone=poi["Phone"],
                location_type=poi["DealerCategory"],
                latitude=poi["Latitude"],
                longitude=poi["Longitude"],
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
