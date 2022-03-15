from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("chickencottage")

locator_domain = "https://chickencottage.com"
base_url = "https://chickencottage.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=74519c906c&load_all=1&layout=1"
_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    with SgRequests() as session:
        store_list = session.get(
            base_url,
            headers=_headers,
        ).json()
        for store in store_list:
            logger.info(store["website"])
            sp1 = bs(session.get(store["website"], headers=_headers).text, "lxml")
            hh = sp1.select_one("div.elementor-slide-description")
            if hh and "You can find your nearest store below" in hh.text:
                continue
            hours = (
                sp1.select("ul.elementor-icon-list-items")[-1]
                .select("li")[-1]
                .text.strip()
            )
            yield SgRecord(
                page_url=store["website"],
                location_name=store["title"],
                street_address=store["street"],
                city=store["city"].replace("LShepherd", "Shepherd"),
                zip_postal=store["postal_code"],
                state=store["state"],
                phone=store["phone"],
                locator_domain=locator_domain,
                country_code=store["country"],
                store_number=store["id"],
                latitude=store["lat"],
                longitude=store["lng"],
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
