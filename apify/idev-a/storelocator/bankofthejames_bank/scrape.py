from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("bankofthejames")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.bankofthejames.bank/"
    base_url = "https://www.bankofthejames.bank/find-a-branch-and-atm/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.bank-location")
        logger.info(f"{len(links)} found")
        for _ in links:
            page_url = base_url
            if _.h5.a:
                page_url = _.h5.a["href"]
            logger.info(page_url)
            addr = parse_address_intl(
                list(_.select_one(".address").stripped_strings)[0]
            )
            if (not addr.state or not addr.city) and page_url != base_url:
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                addr = parse_address_intl(sp1.select_one("p.contact-info-address").text)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            temp = _.select_one("div.more-bank-info div.accord-item").stripped_strings
            hours = []
            for hh in temp:
                if "Holidays" in hh or "residents" in hh or "appointment" in hh.lower():
                    continue
                hours.append(hh.split(", and")[0])
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"].split("-")[-1],
                location_name=_.h5.text.replace("–", "-").strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_.select_one(".phone")
                .text.split("|")[0]
                .replace("Office", "")
                .strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
