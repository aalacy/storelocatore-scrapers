# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.renault.no/admin/index.php?graphql"
    domain = "renault.no"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {
        "operationName": "MyQuery",
        "variables": {},
        "query": "query MyQuery {\n  forhandlere(where: {offsetPagination: {size: 60}}) {\n    nodes {\n      title\n      dealer {\n        depId\n        fylke\n        postnromrademin1\n        postnromrademin2\n        postnromrademin3\n        postnromrademin4\n        postnromrademin5\n        postnromrademin6\n        postnromrademin7\n        postnromrademin8\n        postnromrademin9\n        postnromrademin10\n        postnromrademaks1\n        postnromrademaks2\n        postnromrademaks3\n        postnromrademaks4\n        postnromrademaks5\n        postnromrademaks6\n        postnromrademaks7\n        postnromrademaks8\n        postnromrademaks9\n        postnromrademaks10\n        tjenester\n        lat\n        lng\n        linkToForhandlerside\n        __typename\n      }\n      dealerSideBar {\n        adresse\n        postnummer\n        poststed\n        telefon\n        epost\n        hjemmeside\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
    }
    data = session.post(start_url, headers=hdr, data=frm).json()

    all_locations = data["data"]["forhandlere"]["nodes"]
    for poi in all_locations:
        item = SgRecord(
            locator_domain=domain,
            page_url=poi["dealer"]["linkToForhandlerside"],
            location_name=poi["title"],
            street_address=poi["dealerSideBar"]["adresse"],
            city=poi["dealerSideBar"]["poststed"],
            state=poi["dealer"]["fylke"].capitalize(),
            zip_postal=poi["dealerSideBar"]["postnummer"],
            country_code="NO",
            store_number=poi["dealer"]["depId"],
            phone=poi["dealerSideBar"]["telefon"],
            location_type=", ".join(poi["dealer"]["tjenester"]),
            latitude=poi["dealer"]["lat"],
            longitude=poi["dealer"]["lng"],
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
