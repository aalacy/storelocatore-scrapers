from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.smartbank.com/"
    base_url = "https://www.smartbank.com/locations/"
    json_url = "https://api-cdn.storepoint.co/v1/15a83293917490/locations?rq"
    with SgRequests(verify_ssl=False) as session:
        sp1 = bs(session.get(base_url, headers=_headers).text, "lxml")
        hours = []
        for hh in sp1.select_one("div#main-content p").stripped_strings:
            if "drive" in hh:
                break
            hours.append(hh)
        hr = hours[-2] + hours[-1]
        del hours[-1]
        del hours[-1]
        hours.append(hr)
        locations = session.get(json_url, headers=_headers).json()["results"][
            "locations"
        ]
        for _ in locations:
            addr = parse_address_intl(_["streetaddress"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=base_url,
                location_name=" ".join(bs(_["name"], "lxml").stripped_strings),
                store_number=_["id"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["loc_lat"],
                longitude=_["loc_long"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                raw_address=_["streetaddress"],
                hours_of_operation="; ".join(hours)
                .replace("\xa0", "")
                .replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
