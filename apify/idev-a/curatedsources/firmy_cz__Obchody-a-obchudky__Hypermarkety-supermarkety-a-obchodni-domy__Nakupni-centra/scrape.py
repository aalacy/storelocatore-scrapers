from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://firmy.cz/Obchody-a-obchudky/Hypermarkety-supermarkety-a-obchodni-domy/Nakupni-centra"
base_url = "https://www.firmy.cz/Obchody-a-obchudky/Hypermarkety-supermarkety-a-obchodni-domy/Nakupni-centra"


def _d(_, session):
    page_url = _.h3.a["href"]
    if "detail" not in page_url:
        return None
    logger.info(page_url)
    sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
    raw_address = sp1.select_one("div.detailAddress").text.strip()
    if raw_address.split()[-1] == "2":
        raw_address = " ".join(raw_address.split()[:-1])
    addr = parse_address_intl(raw_address + ", Czech Republic")
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    hours = []
    if sp1.select_one("div.openingTime table"):
        for day in [
            "Pondělí",
            "Úterý",
            "Středa",
            "Čtvrtek",
            "Pátek",
            "Sobota",
            "Neděle",
        ]:
            for hh in sp1.select_one("div.openingTime table").select("tr"):
                if hh.get("class") == ["holidayInfo"]:
                    continue
                td = hh.select("td")
                if td[0].text.strip() == day:
                    hours.append(f"{td[0].text.strip()}: {td[-1].text.strip()}")

    phone = ""
    if sp1.select_one("div.detailPhone"):
        phone = sp1.select_one("div.detailPhone").text.strip()
    return SgRecord(
        page_url=page_url,
        store_number=_.h3.a["data-id"],
        location_name=_.h3.text.strip(),
        street_address=street_address,
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code="Czech Republic",
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours).replace("–", "-"),
        raw_address=raw_address,
    )


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.premiseList div.premiseBox"
        )
        for _ in locations:
            yield _d(_, session)

        page = 2
        while True:
            soup = bs(
                session.get(base_url + f"?page={page}", headers=_headers).text, "lxml"
            )
            locations = soup.select("div.premiseList div.premiseBox")
            if not locations:
                break
            page += 1
            for _ in locations:
                yield _d(_, session)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
