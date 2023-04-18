from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.t-systems.com"
base_url = "https://www.t-systems.com/service/search/ts-gb-en/111596?ajax=true"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["results"]
        for _ in locations:
            city = _["city"]
            state = _.get("state")
            zip_postal = _.get("zipCode")
            country_code = _["countryCode"]
            if country_code == "US":
                zip_postal, city = city, zip_postal
                city = city.replace(",", "")
                c_s = city.split()
                city = " ".join(c_s[:-1])
                state = c_s[-1].strip()
            temp = (_["houseNr"] + " " + _["street"]).strip().split(",")
            street_address = []
            for tt in temp:
                if "Company" in tt:
                    break
                if not tt.strip():
                    continue
                street_address.append(tt)
            yield SgRecord(
                page_url=_.get("url"),
                location_name=_["title"],
                street_address=", ".join(street_address),
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=_["latLong"].split(",")[0].strip(),
                longitude=_["latLong"].split(",")[1].strip(),
                country_code=country_code,
                phone=_.get("telephone"),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
