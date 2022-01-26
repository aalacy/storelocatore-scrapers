from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.hirestation.co.uk"
base_url = "https://www.hirestation.co.uk/branch-locator/data/locations.xml"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "marker"
        )
        for _ in locations:
            try:
                street_address = ""
                if _.get("address1-1"):
                    street_address += " " + _.get("address1-1")
                if _.get("address1"):
                    street_address += " " + _.get("address1")
                addr2 = ""
                if _.get("address2") and "Estate" not in _["address2"]:
                    addr2 = _.get("address2")
                addr3 = ""
                if _.get("address3") and "Estate" not in _["address3"]:
                    addr3 = _.get("address3")
                city = _.get("city")
                if not city:
                    if addr3:
                        city = addr3
                        if addr2:
                            street_address += " " + addr2
                    else:
                        city = addr2
                else:
                    if addr2:
                        street_address += " " + addr2
                    if addr3:
                        street_address += " " + addr3
                hours = []
                if _.get("hours1"):
                    hours.append(_.get("hours1"))
                if _.get("hours2"):
                    hours.append(_.get("hours2"))
                if _.get("hours3"):
                    hours.append(_.get("hours3"))
                yield SgRecord(
                    page_url=_["web"],
                    store_number=_["name"].split("(")[-1].split(")")[0],
                    location_name=_["name"],
                    street_address=street_address,
                    city=city,
                    state=_.get("state"),
                    zip_postal=_["postal"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code="UK",
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
