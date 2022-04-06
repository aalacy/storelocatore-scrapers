from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("millersfresh")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    if (
        val.replace("(", "")
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


def fetch_data():
    locator_domain = "http://www.takefivecafe.ca/"
    base_url = "http://www.takefivecafe.ca/vancouver-coffee-shops-locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("ul#locationtab li a")[1:]
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            pp = [
                list(pp.stripped_strings)
                for pp in sp1.select("div.locationsPage p")
                if pp.text.strip()
            ]
            block = pp[-2]
            phone = block[-1].split(":")[-1].replace("Tel", "").strip()
            if _p(phone):
                del block[-1]
            else:
                phone = ""
            raw_address = " ".join(block).split("(")[0].strip()
            _aa = raw_address.split(",")
            if len(_aa) == 3:
                street_address = _aa[0].strip()
                city = _aa[1].strip()
                state = _aa[2].strip()
                zip_postal = ""
            else:
                addr = parse_address_intl(raw_address + ", Canada")
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                state = addr.state
                zip_postal = addr.postcode
            try:
                coord = sp1.iframe["src"].split("ll=")[1].split("&")[0].split(",")
            except:
                coord = ["", ""]
            hours = []
            for hh in pp[-1]:
                if "Holiday" in hh:
                    break
                hours.append(hh)
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.h1.text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
