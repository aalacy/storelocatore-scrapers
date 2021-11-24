from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("medmark")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://medmark.com/"
    base_url = "https://medmark.com/treatment-locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.all-locations-centers a.location-link")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            try:
                coord = (
                    sp1.select_one(".treatment-map iframe")["data-lazy-src"]
                    .split("!2d")[1]
                    .split("!2m")[0]
                    .split("!3d")[::-1]
                )
            except:
                coord = ["", ""]
            hours = []
            temp = [
                "".join(hh.stripped_strings)
                for hh in sp1.select("div.tc-work div.treatment-work")[0].select(
                    "div.tw-item"
                )
            ]
            for hh in temp:
                if "holiday" in hh.lower():
                    break
                hours.append(hh)
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one('span[itemprop="name"]')
                .text.strip()
                .replace("–", "-"),
                street_address=sp1.select_one(
                    'span[itemprop="streetAddress"]'
                ).text.strip(),
                city=sp1.select_one('span[itemprop="addressLocality"]').text.strip(),
                state=sp1.select_one('span[itemprop="addressRegion"]').text.strip(),
                zip_postal=sp1.select_one('span[itemprop="postalCode"]').text.strip(),
                country_code="US",
                phone=sp1.select_one('span[itemprop="telephone"]').text.strip(),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
