from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.duluxdecoratorcentre.co.uk/"
base_url = "https://www.duluxdecoratorcentre.co.uk/store/getstores?searchQuery=E1+7AE"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["Points"]
        for _ in locations:
            addr = parse_address_intl(_["Address"] + ", United Kingdom")
            try:
                street_address = addr.street_address_1 + ""
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
            except:
                street_address = _["Address"].split(",")[0]
            page_url = locator_domain + _["Url"]
            info = bs(_["FormattedAddress"], "lxml")
            hours = [
                ": ".join(hh.stripped_strings) for hh in info.select("div.store-days")
            ]
            city = addr.city
            if city == "1Fs":
                city = ""
            if "Enfield" in _["Address"]:
                city = "Enfield"
            yield SgRecord(
                page_url=page_url,
                store_number=_["Id"],
                location_name=_["Name"],
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=_["Address"].split(",")[-1],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code="UK",
                phone=_["Telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["Address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
