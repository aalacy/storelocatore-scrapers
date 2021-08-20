from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

locator_domain = "https://www.dunelondon.com"


def fetch_data():
    with SgRequests() as session:
        base_url = "https://www.dunelondon.com/on/demandware.store/Sites-DuneUS-Site/en_US/Stores-FindStores?showMap=false&radius=5000&lat=52.5620475&long=-1.1818485&src=store"
        page_url = "https://www.dunelondon.com/us/en/stores"
        store_list = session.get(base_url).json()["stores"]
        for _ in store_list:
            if _["countryCode"] != "GB":
                continue
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]

            hours = []
            temp = bs(_["storeHours"], "lxml").select("tr")
            for hh in temp:
                td = list(hh.stripped_strings)
                if len(td) == 4:
                    hours.append(f"{td[0]}: {td[1]}:{td[2]}:{td[3]}")
                else:
                    hours.append(f"{td[0]}: {td[1]}")

            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                zip_postal=_["postalCode"],
                store_number=_["ID"],
                country_code=_["countryCode"],
                locator_domain=locator_domain,
                latitude=_["latitude"],
                longitude=_["longitude"],
                phone=_.get("phone"),
                hours_of_operation=" ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
