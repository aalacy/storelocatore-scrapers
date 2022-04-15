from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data():
    locator_domain = "https://astonmartin.co.uk"
    with SgRequests() as session:
        res = session.get(
            "https://www.astonmartin.com/api/v1/dealers?latitude=51.5113555&longitude=-0.1568901000000551&cultureName=en-GB&take=1000"
        )
        for store in res.json():
            if store["Address"]["CountryCode"] != "United Kingdom":
                continue
            page_url = (
                locator_domain + store["DealerPageUrl"]
                if store["DealerPageUrl"] is not None
                else SgRecord.MISSING
            )
            yield SgRecord(
                page_url=page_url,
                locator_domain=locator_domain,
                location_name=store["Name"],
                street_address=store["Address"]["Street"],
                city=store["Address"]["City"],
                state=store["Address"]["StateCode"],
                zip_postal=store["Address"]["Zip"],
                phone=store["PhoneNumber"],
                country_code=store["Address"]["CountryCode"],
                store_number=store["DCSId"],
                latitude=store["Address"]["Latitude"],
                longitude=store["Address"]["Longitude"],
                hours_of_operation="; ".join(store["OpeningHours"]).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
