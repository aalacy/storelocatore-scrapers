from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://myfavoritemuffin.com"
base_url = "https://myfavoritemuffin.com/Umbraco/Api/LocationsApi/GetNearbyLocations?latitude=40.0711202976&longitude=-116.598821819119&maxResults=&maxDistance=5000"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for store in locations:
            sp1 = bs(store["HtmlRow"], "lxml")
            street_address = store["Address1"] or ""
            if store["Address2"]:
                street_address += " " + store["Address2"]
            page_url = ""
            if sp1.select_one("div.links a.btn"):
                page_url = sp1.select_one("div.links a.btn")["href"]
                if not page_url.startswith("http"):
                    page_url = (
                        locator_domain + sp1.select_one("div.links a.btn")["href"]
                    )

            yield SgRecord(
                page_url=page_url,
                store_number=store["ID"],
                location_name=sp1.select_one(".name").text.strip(),
                street_address=street_address,
                city=store["Locality"],
                state=store["Region"],
                zip_postal=store["PostalCode"],
                latitude=store["Latitude"],
                longitude=store["Longitude"],
                country_code="US",
                phone=store["Phone"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
