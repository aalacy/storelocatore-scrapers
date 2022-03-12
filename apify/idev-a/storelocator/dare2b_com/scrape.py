from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.dare2b.com/"
base_url = "https://www.dare2b.com/rest/db_uk/V1/locator/?searchCriteria%5Bscope%5D=store-locator&searchCriteria%5Blatitude%5D=32.7254&searchCriteria%5Blongitude%5D=-97.3208&searchCriteria%5Bcurrent_page%5D=1&searchCriteria%5Bpage_size%5D=2000"


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

            page_url = f"https://www.dare2b.com/store-finder/store_page/view/id/{_['store_id']}/"
            hours = []
            for hh in _["opening_hours"]:
                hours.append(f"{hh['day']}: {hh['hours']}")

            country_code = addr["country"]
            zip_postal = addr["postcode"]
            if zip_postal == "n/a":
                zip_postal = ""
            if country_code == "UG":
                country_code = "GB"

            street_address = ", ".join(_ss)
            raw_address = (
                f"{street_address}, {city}, {state}, {zip_postal}, {country_code}"
            )
            yield SgRecord(
                page_url=page_url,
                store_number=_["store_id"],
                location_name=_["name"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=_["geolocation"]["latitude"],
                longitude=_["geolocation"]["longitude"],
                country_code=country_code,
                phone=_["tel"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
