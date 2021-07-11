from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.lynnsdakotamart.com/"
    base_url = "https://www.lynnsdakotamart.com/storelocator"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = json.loads(
            res.split("globalConfig.data =")[1]
            .encode("utf8")
            .decode()
            .split('<script src="https://ajax')[0]
            .strip()[:-11]
            .replace("scr\\ipt", "script")
        )
        for _ in locations["StoreList"]:
            street_address = _["PrimaryAddress"]
            if _["SecondaryAddress"]:
                street_address += " " + _["SecondaryAddress"]
            if street_address.endswith(","):
                street_address = street_address[:-1]
            yield SgRecord(
                page_url=base_url,
                store_number=_["StoreNumber"],
                location_name=_["StoreName"],
                street_address=street_address,
                city=_["City"],
                state=_["LinkState"]["Abbreviation"],
                zip_postal=_["PostalCode"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code="US",
                phone=_["Phone"],
                locator_domain=locator_domain,
                hours_of_operation=_["OpenHoursDisplay"]
                .replace("|", ";")
                .replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
