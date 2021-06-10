from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests


def fetch_data():
    locator_domain = "https://www.astonmartin.com/"
    with SgRequests() as session:
        res = session.get(
            "https://www.astonmartin.com/api/v1/dealers?latitude=51.5113555&longitude=-0.1568901000000551&cultureName=en-GB&take=26"
        )
        for store in res.json():
            page_url = (
                locator_domain + store["DealerPageUrl"]
                if store["DealerPageUrl"] is not None
                else "<MISSING>"
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
