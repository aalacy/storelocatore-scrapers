# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.scandinavian.com.ar/_v/private/graphql/v1?workspace=master&maxAge=long&appsEtag=remove&domain=store&locale=es-AR"
    domain = "scandinavian.com.ar"
    hdr = {
        "accept": "*/*",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    }
    frm = {
        "operationName": "getStores",
        "variables": {},
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "43c4c6a895c8c8f4a69ab48dbad5fcfc1d37f0a089f62b8b6dc32f20134c2810",
                "sender": "vtex.store-locator@0.x",
                "provider": "vtex.store-locator@0.x",
            }
        },
    }
    data = session.post(start_url, headers=hdr, json=frm).json()

    for poi in data["data"]["getStores"]["items"]:

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.scandinavian.com.ar/tiendas",
            location_name=poi["name"],
            street_address=poi["address"]["street"] + " " + poi["address"]["number"],
            city=poi["address"]["city"],
            state=poi["address"]["state"],
            zip_postal=poi["address"]["postalCode"],
            country_code="AR",
            store_number=poi["id"],
            phone="",
            location_type="",
            latitude=poi["address"]["location"]["latitude"],
            longitude=poi["address"]["location"]["longitude"],
            hours_of_operation="",
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
