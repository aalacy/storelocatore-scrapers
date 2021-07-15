from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("victrolacoffee")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.victrolacoffee.com"
base_url = "https://www.victrolacoffee.com/pages/locations"


def _p(val):
    return (
        val.replace("Call", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.shg-c-lg-6")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = [
                hh.text.strip().split("(")[0]
                for hh in sp1.select("div.shg-theme-text-content p")
                if hh.text.strip()
            ][1:]
            phone = ""
            if _p(hours[-1]):
                phone = hours[-1]
                del hours[-1]
            street_address = sp1.select_one("h1.page-title").text.strip()
            city = state = zip_postal = ""
            if "Open" not in hours[0] and "Monday" not in hours[0]:
                addr = hours[0].replace("map", "")
                street_address = hours[0].split("--")[0].strip()
                city = hours[0].split("--")[1].split(",")[0].strip()
                state = (
                    hours[0].split("--")[1].split(",")[1].strip().split(" ")[0].strip()
                )
                zip_postal = (
                    hours[0].split("--")[1].split(",")[1].strip().split(" ")[1].strip()
                )
                del hours[0]
            coord = (
                sp1.select_one("div.shg-c iframe")["src"]
                .split("!2d")[1]
                .split("!2m")[0]
                .split("!3d")
            )
            yield SgRecord(
                page_url=page_url,
                location_name=link.h1.text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                phone=phone.replace("Call", ""),
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
