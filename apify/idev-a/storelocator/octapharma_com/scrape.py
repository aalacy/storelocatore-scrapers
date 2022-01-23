from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.octapharma.com"
base_url = "https://www.octapharma.com/about-us/our-locations/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("script#__NEXT_DATA__")
            .string
        )["props"]["pageProps"]["content"]["components"][0]["data"]
        for _ in locations:
            info = _["content"]
            _cc = info["city"].split(",")
            state = ""
            if len(_cc) > 1:
                state = _cc[-1]
            country_code = info["country"][0]
            city = _cc[0]
            zip_postal = info["postalCode"]
            if country_code == "United Kingdom":
                city, zip_postal = zip_postal, city

            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=info["address"],
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=info["latitude"],
                longitude=info["longitude"],
                country_code=country_code,
                phone=info["phone"],
                location_type=info["type"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
