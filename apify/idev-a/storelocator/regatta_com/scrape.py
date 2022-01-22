from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.regatta.com/"
base_url = "https://www.regatta.com/rest/rg_uk/V1/locator/?searchCriteria%5Bscope%5D=store-locator&searchCriteria%5Blatitude%5D=43.6319&searchCriteria%5Blongitude%5D=-79.3716&searchCriteria%5Bcurrent_page%5D=2&searchCriteria%5Bpage_size%5D=2000"

us_url = "https://backend-regatta-us.basecamp-pwa-prod.com/api/ext/store-locations/search?lat1=62.24128219987466&lng1=-171.86167175000003&lat2=-7.767694768368658&lng2=-64.63510925000001"


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

            country_code = addr["country"]
            zip_postal = addr["postcode"]
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

        locations = session.get(us_url, headers=_headers).json()["result"]["hits"][
            "hits"
        ]
        for loc in locations:
            _ = loc["_source"]
            street_address = _["street"]
            if _["street_line_2"]:
                street_address += " " + _["street_line_2"]

            hours = []
            hh = json.loads(_["opening_hours"])
            for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
                day = day.lower()
                start = hh.get(f"{day}_from")
                end = hh.get(f"{day}_to")
                hours.append(f"{day}: {start} - {end}")

            raw_address = f"{street_address}, {_['city']}, {_['region']}, {_['postcode']}, {_['country']}"
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url="https://www.regatta.com/us/store-locator/",
                store_number=_["store_id"],
                location_name=_["name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["location"]["lat"],
                longitude=_["location"]["lon"],
                country_code=_["country"],
                phone=_["telephone"],
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
