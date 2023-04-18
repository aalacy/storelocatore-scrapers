from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.toysrus.com.cn"
base_url = "https://www.toysrus.com.cn/en-cn/stores/"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _coord(locs, name):
    for loc in locs:
        if loc["name"] == name:
            return loc


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        sp1 = bs(session.get(base_url, headers=_headers).text, "lxml")
        locs = json.loads(sp1.select_one("div.map-canvas")["data-locations"])
        locations = sp1.select("div.store.store-item")
        for _ in locations:
            street_address = _["data-store-address1"]
            if _["data-store-address2"]:
                street_address += " " + _["data-store-address2"]
            addr = street_address.split(",")
            if "China" in addr[-1]:
                del addr[-1]
            state = _["data-store-statecode"]
            city = _["data-store-city"]
            zip_postal = _["data-store-postalcode"]

            raw_address = f"{street_address}, {city}, {state}"
            _ss = addr[-1].lower()
            if (
                "province" in _ss
                or "jilin" in _ss
                or "shandong" in _ss
                or "dalian" in _ss
                or "zhejiang" in _ss
                or "fujian" in _ss
                or "sichuan" in _ss
                or "shaanxi" in _ss
                or "henan" in _ss
                or "hunan" in _ss
                or "hubei" in _ss
                or "yunnan" in _ss
                or "gunagxi" in _ss
                or "shanxi" in _ss
                or "anhui" in _ss
                or "jiangxi" in _ss
                or "inner mongolia" in _ss
                or "guangdong" in _ss
                or "jiangsu" in _ss
                or "zhongshan" in _ss
                or "liaoning" in _ss
                or "heilongjiang" in _ss
                or "guangxi" in _ss
                or "hebei" in _ss
                or "beijng" in _ss
            ):
                if not state:
                    state = addr[-1]
                del addr[-1]

            _cc = addr[-1].lower().replace(" ", "").replace("'", "").replace("’", "")
            c_t = _["data-store-city"].replace("'", "").replace("’", "").lower()
            if c_t in _cc:
                del addr[-1]

            if not addr and len(street_address.split(",")) == 1:
                addr = street_address.split(",")

            if addr and ("Room" in addr[0] or "Area" in addr[0]):
                del addr[0]

            street_address = ", ".join(addr)
            _street = street_address.split()
            for x, aa in enumerate(_street):
                if "district" in aa.lower():
                    street_address = " ".join(_street[: x - 1])

            if street_address.endswith(","):
                street_address = street_address[:-1]

            hours = []
            temp = {}
            for hh in bs(_["data-store-details"], "lxml").select(
                "div.store-hours div.row"
            ):
                cols = hh.select("div.col-auto")
                temp[cols[0].text.strip()] = " ".join(cols[1].stripped_strings)
            for day in days:
                day = day.lower()
                times = "closed"
                if temp.get(day):
                    times = temp.get(day)
                hours.append(f"{day}: {times}")

            coord = _coord(locs, _["data-store-name"])
            yield SgRecord(
                page_url=base_url,
                store_number=_["data-store-id"].replace("store", ""),
                location_name=_["data-store-name"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="China",
                latitude=coord["latitude"],
                longitude=coord["longitude"],
                location_type="toysrus",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
