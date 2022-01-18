from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("kipling")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kipling.asia"
base_url = "https://www.kipling.asia/kipling-stores/"

cc_maps = {
    "PH": "Philippines",
    "ID": "Indonesia",
    "MY": "Malaysia",
    "SG": "Singapore",
    "HK": "Hong Kong",
    "TW": "Taiwan",
    "CN": "China",
}


def parse_china(raw_address):
    raw_address = raw_address.replace("中国", "")
    state = city = street_address = ""
    if "澳门" in raw_address:
        city = "澳门"
        street_address = raw_address.replace("澳门", "")
    if "香港" in raw_address:
        city = "香港"
        street_address = raw_address.replace("香港", "")
    if "省" in raw_address:
        state = raw_address.split("省")[0] + "省"
        raw_address = raw_address.split("省")[-1]
    if "自治区" in raw_address:
        state = raw_address.split("自治区")[0] + "自治区"
        raw_address = raw_address.split("自治区")[-1]
    if "内蒙古" in raw_address:
        state = "内蒙古"
        raw_address = raw_address.replace("内蒙古", "")
    if "自治州" in raw_address:
        state = raw_address.split("自治州")[0] + "自治州"
        raw_address = raw_address.split("自治州")[-1]

    if "路" in city:
        _cc = city.split("路")
        city = _cc[-1]
        street_address = _cc[0] + "路" + street_address
    if "号" in city:
        _cc = city.split("号")
        city = _cc[-1]
        street_address = _cc[0] + "号" + street_address
    if "区" in city:
        _cc = city.split("区")
        city = _cc[-1]
        street_address = _cc[0] + "区" + street_address

    if "市" in raw_address:
        _ss = raw_address.split("市")
        street_address = _ss[-1]
        city = _ss[0]
        if "市" not in city:
            city += "市"

    return state, city, street_address


def fetch_data():
    with SgRequests() as session:
        sp1 = bs(session.get(base_url, headers=_headers).text, "lxml")
        country_map = {}
        for cc in sp1.select("select#districtSelector option.address-item"):
            if not cc.get("data-area"):
                continue
            country_map[cc["value"]] = cc_maps[cc["data-area"]]
        locations = sp1.select("li.address-item")
        for _ in locations:
            raw_address = _.select_one("div.address").text.strip()
            if not raw_address:
                continue
            country = country_map[_["data-area"]]
            state = zip_postal = city = street_address = ""
            if country in ["China", "Taiwan"]:
                state, city, street_address = parse_china(raw_address)
            else:
                addr = parse_address_intl(raw_address + ", " + country)
                street_address = addr.street_address_1 or ""
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                state = addr.state
                zip_postal = addr.postcode
            if city and city.isdigit():
                city = ""
            if country == "Indonesia":
                if state == "02A":
                    city = ""
            phone = (
                _.find("div", string=re.compile(r"PHONE"))
                .find_next_sibling()
                .text.strip()
            )

            hours = "; ".join(
                _.find("div", string=re.compile(r"OPENING HOUR"))
                .find_next_sibling()
                .stripped_strings
            )

            yield SgRecord(
                page_url=base_url,
                store_number=_["data-id"],
                location_name="Kipling",
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country,
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours.replace("\n", "; ").replace("\r", ""),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
