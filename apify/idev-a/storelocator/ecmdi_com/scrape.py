from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["", "Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def fetch_data():
    base_url = "https://www.ecmdi.com/branch-locator/"
    locator_domain = "https://www.ecmdi.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        scripts = soup.find_all("script", type="text/x-magento-init")
        locations = []
        for _ in scripts:
            if _.string.strip():
                script = json.loads(_.string.strip())
                if "*" in script:
                    if "Magento_Ui/js/core/app" in script["*"]:
                        if "components" in script["*"]["Magento_Ui/js/core/app"]:
                            if (
                                "storeLocator"
                                in script["*"]["Magento_Ui/js/core/app"]["components"]
                            ):
                                if (
                                    "branches"
                                    in script["*"]["Magento_Ui/js/core/app"][
                                        "components"
                                    ]["storeLocator"]
                                ):
                                    locations = script["*"]["Magento_Ui/js/core/app"][
                                        "components"
                                    ]["storeLocator"]["branches"]
                                    break

        for aa, _ in locations.items():
            hours = []
            for key, value in _["formatted_hours"].items():
                time = f"{value['open']}-{value['close']}"
                if not value["isOpen"]:
                    time = "closed"
                hours.append(f"{days[int(key)]}: {time}")

            yield SgRecord(
                page_url=base_url,
                store_number=_["branch_id"],
                location_name=_["branch_name"],
                street_address=f"{_['address']['address_1']} {_['address'].get('address_2')} {_['address'].get('address_3')}",
                city=_["address"]["city"],
                state=_["address"]["region_code"],
                zip_postal=_["address"]["postcode"],
                phone=_["phone"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["address"]["country"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
