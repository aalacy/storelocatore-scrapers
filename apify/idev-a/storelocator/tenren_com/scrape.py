from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import bs4
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tenren")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.tenren.com/"
base_url = "https://www.tenren.com/store-locations.html"
data = []


def _p(val):
    if (
        val.split(":")[-1]
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def _fill(page_url, country, location_name, _addr, phone, hours):
    if len(_addr) == 1:
        _addr = [location_name] + _addr

    raw_address = " ".join(_addr).replace(".", " ")
    raw_address = raw_address.replace("N Y", "NY").replace("N S W", "NSW")
    addr = parse_address_intl(raw_address)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    data.append(
        SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=country.text.strip(),
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours,
            raw_address=raw_address,
        )
    )

    logger.info(f"{location_name} scraped")

    return True


def _d(page_url, loc, country):
    location_name = phone = hours = ""
    _addr = []
    if len(loc.contents) == 1:
        info = list(loc.stripped_strings)
        location_name = info[0]
        if info[-1].startswith("Open"):
            hours = info[-1]
            del info[-1]
        if _p(info[-1]):
            phone = info[-1]
            del info[-1]
        _addr = info[1:]
        _fill(page_url, country, location_name, _addr, phone, hours)
    else:
        for x, _ in enumerate(loc.contents):
            if location_name and isinstance(_, bs4.element.NavigableString):
                if _.strip():
                    if phone and _.strip().startswith("Open"):
                        hours = _.strip()
                    if "Tel:" in _:
                        phone = _.replace("Tel:", "").split("Fax")[0].strip()
                    if not phone and "Tel" not in _ and "Fax" not in _:
                        _addr.append(_.replace("\n", " ").strip())

            if isinstance(_, bs4.element.Tag) and _p(_.text.strip()):
                phone = _.text.strip()

            if not location_name:
                if isinstance(_, bs4.element.NavigableString):
                    if (
                        _.next_sibling
                        and _.next_sibling.name == "a"
                        and "www.mapquest.com" in _.next_sibling["href"]
                    ):
                        location_name = _.replace("\n", " ").strip()

                    elif x == 0:
                        location_name = _.replace("\n", " ").strip()

                    elif _.previous_sibling and _.previous_sibling.name == "br":
                        if _.previous_sibling.previous_sibling.name == "br":
                            location_name = _.replace("\n", " ").strip()
                        if (
                            _.previous_sibling.previous_sibling == "\n"
                            and _.previous_sibling.previous_sibling.previous_sibling.name
                            == "br"
                        ):
                            location_name = _.replace("\n", " ").strip()
                    else:
                        pass

                elif isinstance(_, bs4.element.Tag):
                    if _.name == "b" or _.name == "a" or _.name == "font":
                        location_name = _.text.replace("\n", " ").strip()

            if location_name and _addr:
                scraped = False

                if x == len(loc.contents) - 1 or x == len(loc.contents) - 2:
                    scraped = _fill(
                        page_url, country, location_name, _addr, phone, hours
                    )
                elif _.next_sibling.name == "p":
                    scraped = _fill(
                        page_url, country, location_name, _addr, phone, hours
                    )
                elif isinstance(_, bs4.element.Tag):
                    if _.name == "br":
                        if _.next_sibling.name == "br":
                            scraped = _fill(
                                page_url, country, location_name, _addr, phone, hours
                            )
                        elif (
                            _.next_sibling == "\n"
                            and _.next_sibling.next_sibling.name == "br"
                        ):
                            scraped = _fill(
                                page_url, country, location_name, _addr, phone, hours
                            )
                        else:
                            logger.info("----- br")

                if scraped:
                    location_name = phone = hours = ""
                    _addr = []

            if isinstance(_, bs4.element.Tag) and not location_name and _.name == "p":
                _d(page_url, _, country)


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        countries = soup.select("div.fsection-caption table a")
        for country in countries:
            country_url = locator_domain + country["href"]
            logger.info(country_url)
            res = session.get(country_url, headers=_headers)
            if res.url == locator_domain:
                continue
            sp1 = bs(res.text, "lxml")
            states = sp1.select("div.fsection-caption table a")
            if states:
                for state in states:
                    state_url = locator_domain + state["href"]
                    logger.info(state_url)
                    sp2 = bs(session.get(state_url, headers=_headers).text, "lxml")
                    _d(state_url, sp2.select_one("div.fsection-caption"), country)

            else:
                _d(country_url, sp1.select_one("div.fsection-caption"), country)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data()
        for rec in data:
            writer.write_row(rec)
