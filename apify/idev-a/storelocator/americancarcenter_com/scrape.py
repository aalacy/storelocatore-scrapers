from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.americancarcenter.com"
base_url = (
    "https://www.americancarcenter.com/_next/data/oMHfqGEOU4KH1G1SPCekV/contact-us.json"
)


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["pageProps"][
            "initialDealershipState"
        ]["dealerships"]
        for _ in locations:
            page_url = f"https://www.americancarcenter.com/dealership-detail/{_['city']}-{_['state']}-{'-'.join(_['address'].upper().split())}-{_['id']}"
            hours = []
            for day, hh in _["schedule"].items():
                hours.append(f"{day}: {hh}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                country_code="US",
                phone=_["phone"] if _["phone"] else _["phone2"],
                latitude=_["lat"],
                longitude=_["long"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
