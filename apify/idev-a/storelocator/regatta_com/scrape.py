from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = ""
base_url = "https://www.regatta.com/rest/rg_uk/V1/locator/?searchCriteria%5Bscope%5D=store-locator&searchCriteria%5Blatitude%5D=43.6319&searchCriteria%5Blongitude%5D=-79.3716&searchCriteria%5Bcurrent_page%5D=2&searchCriteria%5Bpage_size%5D=2000"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["locations"]
        for _ in locations:
            addr = _["address"]
            street_address = addr["line"]
            if type(addr["line"]) == list:
                street_address = " ".join(addr["line"])

            _cc = addr["city"].split(",")
            city = _cc[0].strip()
            state = ""
            if len(_cc) > 1:
                state = _cc[1].strip()
            _ss = []
            for st in street_address.split(","):
                if (
                    st.strip().lower().startswith(city.lower())
                    and "center" not in st.lower()
                    and "centre" not in st.lower()
                    and "park" not in st.lower()
                ):
                    break
                _ss.append(st)

            page_url = f"https://www.regatta.com/store-finder/store_page/view/id/{_['store_id']}/"
            hours = []
            for hh in _["opening_hours"]:
                hours.append(f"{hh['day']}: {hh['hours']}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["store_id"],
                location_name=_["name"],
                street_address=", ".join(_ss),
                city=city,
                state=state,
                zip_postal=addr["postcode"],
                latitude=_["geolocation"]["latitude"],
                longitude=_["geolocation"]["latitude"],
                country_code=addr["country"],
                phone=_["tel"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
