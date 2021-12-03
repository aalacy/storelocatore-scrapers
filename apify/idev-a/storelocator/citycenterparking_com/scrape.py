from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("citycenterparking")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.citycenterparking.com/"
base_url = "https://ccplots.myparkingworld.com/api/lots/CCP/EN?latLoc=45.5230622&lngLoc=-122.6764816&latMin=43.69306840763678&lngMin=-133.0036300375&latMax=47.29540987350418&lngMax=-112.34933316249999&csr=0&branchName="


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = _["address"]
            street_address = addr["address1"]
            if addr["address2"]:
                street_address += " " + addr["address2"]
            page_url = f"https://ccplots.myparkingworld.com/CCP/en?latlng=45.5230622,-122.67648159999999&_ga=2.90973594.1063415383.1632952321-737608664.1632952321#details=61,{_['lotNumber']}"
            location_type = "daily"
            if _["hasMonthlyRates"]:
                location_type = "monthly"
            url = f"https://ccplots.myparkingworld.com/CCP/EN/details/61/{_['lotNumber']}?csr=0"
            logger.info(url)
            sp1 = bs(session.get(url, headers=_headers).text, "lxml")
            coord = (
                sp1.select_one("div#staticMapCanvas a")["href"]
                .split("%7C")[1]
                .split("&")[0]
                .split(",")
            )
            yield SgRecord(
                page_url=page_url,
                store_number=_["lotNumber"],
                location_name=_["lotName"],
                street_address=street_address,
                city=addr["city"],
                state=addr["provState"],
                zip_postal=addr["postalCode"],
                latitude=coord[0],
                longitude=coord[1],
                country_code=addr["country"],
                location_type=location_type,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
