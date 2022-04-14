from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("lionsden")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.lionsden.com/"
base_url = "https://www.lionsden.com/amlocator/index/ajax/?p={}&lat=40.078872&lng=-82.9447782&radius=0&product=0&category=0&attributes%5B0%5D%5Bname%5D=7&attributes%5B0%5D%5Bvalue%5D=&attributes%5B1%5D%5Bname%5D=16&attributes%5B1%5D%5Bvalue%5D=&attributes%5B2%5D%5Bname%5D=19&attributes%5B2%5D%5Bvalue%5D=&attributes%5B3%5D%5Bname%5D=22&attributes%5B3%5D%5Bvalue%5D=&attributes%5B4%5D%5Bname%5D=23&attributes%5B4%5D%5Bvalue%5D=&sortByDistance=false"


def _hoo(blocks, id):
    ss = None
    for block in blocks:
        if block["data-amid"] == str(id):
            ss = block
            break
    return ss


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        page = 1
        first_loc = None
        should_break = False
        while True:
            res = session.get(base_url.format(page), headers=_headers).json()
            blocks = bs(res["block"], "lxml").select("div.amlocator-store-desc")
            locations = res["items"]
            logger.info(f"page {page} {len(locations)}")
            for _ in locations:
                if page == 1:
                    first_loc = _
                elif first_loc["id"] == _["id"]:
                    should_break = True
                block = _hoo(blocks, _["id"])
                page_url = f"https://www.lionsden.com/storelocator/store-{_['id']}/"
                hours = []
                for hh in block.select(
                    "div.amlocator-schedule-table div.amlocator-row"
                ):
                    if "HOLIDAY" in hh.text:
                        continue
                    if "**" in hh.text:
                        continue
                    hours.append(": ".join(hh.stripped_strings))
                info = [
                    pp.text.strip()
                    for pp in block.select("div.amlocator-store-information p")
                ]
                raw_address = " ".join(info[:2])
                addr = parse_address_intl(raw_address + ", USA")
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2

                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=block.select_one("div.amlocator-title").text.strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code="US",
                    phone=_p(info[2]),
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )

            if locations:
                page += 1

            if should_break:
                break


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=10
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
