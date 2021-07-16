from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("softrontax")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.softrontax.com/"
    base_url = "https://www.softrontax.com/location-ajax/"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            page_url = _["website"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = [hh.text.strip() for hh in sp1.select("ul.sloc_hours_list li")]
            cnt = 0
            for hh in hours:
                if "closed" in hh.split(":")[-1].lower():
                    cnt += 1
            if cnt == 7:
                hours = ["Closed"]
            yield SgRecord(
                page_url=page_url,
                location_name=_["locname"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
