from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.stagshop.com/"
base_url = "https://stagshop.com/pages/store-locations"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#storeItemsWrap div.storeItemWrap")
        for _ in locations:
            if "coming-soon" in _.img["src"]:
                continue
            addr = list(_.select_one("div.storeAddressLeft").stripped_strings)
            try:
                coord = (
                    _.select_one("div.storeGoogleMapsLink a")["href"]
                    .split("ll=")[1]
                    .split("&s")[0]
                    .split(",")
                )
            except:
                try:
                    coord = (
                        _.select_one("div.storeGoogleMapsLink a")["href"]
                        .split("/@")[1]
                        .split("z/data")[0]
                        .split(",")
                    )
                except:
                    coord = ["", ""]

            hours = [
                hh.text.strip()
                for hh in _.select_one("div.storeHoursRight").findChildren(
                    recursive=False
                )
                if hh.text.strip() and "HOUR" not in hh.text
            ]
            phone = addr[1]
            if "@" in phone:
                phone = ""
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_.select_one("div.storeNameWrap").text,
                street_address=addr[-2],
                latitude=coord[0],
                longitude=coord[1],
                zip_postal=addr[-1],
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
