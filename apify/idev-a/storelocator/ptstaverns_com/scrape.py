from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ptstaverns")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _v(val):
    return val.replace("’", "'").strip()


def fetch_data():
    locator_domain = "https://www.ptstaverns.com"
    base_url = "https://www.ptstaverns.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        logger.info(f'{len(locations["markers"])} found')
        for _ in locations["markers"]:
            addr = parse_address_intl(_["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            page_url = _["link"]
            if not page_url.startswith("https"):
                page_url = locator_domain + _["link"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours_of_operation = ""
            hours = [
                hh.text.strip() for hh in sp1.select("div.et_pb_blurb_container > h4")
            ][::-1]
            for x, hh in enumerate(hours):
                if "View Menu" in hh:
                    if "Kitchen" in hours[x + 1]:
                        hours_of_operation = hours[x + 2]
                    else:
                        hours_of_operation = hours[x + 1]
                    break
            yield SgRecord(
                page_url=page_url,
                location_name=_v(_["title"]),
                store_number=_["id"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=bs(_["description"], "lxml").text.strip(),
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
