from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("barrio")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://barrio-tacos.com/"
    base_url = "https://barrio-tacos.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.content.location")
        for _ in locations:
            page_url = "https://barrio-tacos.com" + _.select_one("span.links a")["href"]
            addr = parse_address_intl(_.select_one("span.location-address").text)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            if sp1.select_one("div.temporarily-closed"):
                hours = ["Temporarily closed"]
            else:
                for hh in sp1.select("div.office-hours__item"):
                    hours.append(
                        f"{hh.select_one('.office-hours__item-label').text}{hh.select_one('.office-hours__item-slots').text}"
                    )
            logger.info(page_url)
            phone = ""
            if _.select_one("span.location-phone"):
                phone = _.select_one("span.location-phone").text
            yield SgRecord(
                page_url=page_url,
                location_name=_.select_one("span.location-name").text,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                locator_domain=locator_domain,
                phone=phone,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
