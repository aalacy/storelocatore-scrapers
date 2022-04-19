from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefourarmenia.com"
urls = {
    "Armenia": "https://www.carrefourarmenia.com/en/store-locator/search-store?title=&title2=",
    "Bahrain": "https://www.carrefourbahrain.com/en/store-locator/search-store?title=&title2=",
    "Oman": "https://www.carrefouroman.com/en/store-locator/search-store?title=&title2=",
}


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            soup = bs(session.get(base_url, headers=_headers).text, "lxml")
            locations = soup.select("div.stores-lists-dir")
            for _ in locations:
                addr = [
                    aa.strip()
                    for aa in _.select_one("span.city-addr")
                    .text.replace(",", " ")
                    .replace("،", "")
                    .strip()
                    .split()
                    if aa.strip()
                ]
                raw_address = ", ".join(addr)
                street_address = city = zip_postal = ""
                if country.lower() in addr[-1].lower():
                    del addr[-1]
                c_idx = -2
                if addr[-1].replace("/", "").isdigit():
                    zip_postal = addr[-1]
                else:
                    c_idx += 1

                city = addr[c_idx]
                street_address = " ".join(addr[:c_idx])

                yield SgRecord(
                    page_url=base_url,
                    store_number=_["data-id"],
                    location_name=_.h4.text.strip(),
                    street_address=street_address.replace("Bahrain", ""),
                    city=city,
                    zip_postal=zip_postal,
                    country_code=country,
                    location_type=_.select_one("span.shop").text.strip(),
                    latitude=_.a["data-lat"],
                    longitude=_.a["data-lat"],
                    locator_domain=locator_domain,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
