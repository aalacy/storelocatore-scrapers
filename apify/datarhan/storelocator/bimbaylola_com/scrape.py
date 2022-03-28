# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.bimbaylola.com/on/demandware.store/Sites-byl-ic-Site/en_AD/Stores-FindStores?isForm=false&showMap=true&lat=&long=&countryCode={}&radius=20000"
    domain = "bimbaylola.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get("https://www.bimbaylola.com/ic_en/stores")
    dom = etree.HTML(response.text)
    all_countries = dom.xpath('//select[@name="country"]/option/@value')
    for country in all_countries:
        data = session.get(start_url.format(country), headers=hdr).json()
        for poi in data["stores"]:
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.bimbaylola.com/ic_en/stores",
                location_name=poi["name"],
                street_address=street_address,
                city=poi["city"],
                state="stateCode",
                zip_postal=poi["postalCode"],
                country_code=poi["countryCode"],
                store_number=poi["ID"],
                phone=poi.get("phone"),
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=" ".join(
                    poi["storeHours"]
                    .replace("WE ARE OPEN!", "")
                    .split("WhatsApp")[0]
                    .split()
                ),
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
