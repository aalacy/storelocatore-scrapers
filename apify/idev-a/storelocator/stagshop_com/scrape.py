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
            href = _.select_one("div.storeGoogleMapsLink a")["href"]
            raw_address = state = ""
            try:
                raw_address = (
                    href.split("hnear=")[1]
                    .split("&")[0]
                    .split("d6c2c447971,")[-1]
                    .replace("+", " ")
                )
            except:
                try:
                    raw_address = href.split("?q=")[1].split("&")[0].replace("+", " ")
                except:
                    try:
                        raw_address = (
                            href.split("place/")[1]
                            .split("/@")[0]
                            .split("/data")[0]
                            .replace("+", " ")
                        )
                    except:
                        try:
                            raw_address = (
                                href.split("dir//")[1]
                                .split("/@")[0]
                                .split()[0]
                                .replace("+", " ")
                            )
                        except:
                            pass
            try:
                coord = href.split("ll=")[1].split("&s")[0].split(",")
            except:
                try:
                    coord = href.split("/@")[1].split("z/data")[0].split(",")
                except:
                    coord = ["", ""]

            hours = [
                hh.text.strip()
                for hh in _.select_one("div.storeHoursRight").findChildren(
                    recursive=False
                )
                if hh.text.strip() and "HOUR" not in hh.text and "APRIL" not in hh.text
            ]
            phone = addr[1]
            if "@" in phone:
                phone = ""
            location_name = _.select_one("div.storeNameWrap").text.strip()
            _cc = location_name.split()
            if _cc[-1].strip().isdigit():
                del _cc[-1]

            raw_address = (
                raw_address.replace("%5C", "")
                .replace("%27", "'")
                .replace("/", "")
                .replace("%236", "#236")
            )
            if raw_address:
                state = raw_address.split(",")[-1].strip().split()[0]
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=location_name,
                street_address=addr[-2],
                city=" ".join(_cc),
                state=state,
                zip_postal=addr[-1],
                country_code="CA",
                latitude=coord[0],
                longitude=coord[1],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
