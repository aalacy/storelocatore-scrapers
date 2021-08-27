from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("valero")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.valero.com"
base_url = "https://www.valero.com/about/locations?location_type_id=1&page={}"


def fetch_data():
    with SgRequests() as session:
        page = 0
        while True:
            links = bs(
                session.get(base_url.format(page), headers=_headers).text, "lxml"
            ).select("section#block-valero-content div.content-item")
            if not links:
                break
            page += 1
            logger.info(f"{len(links)} found")
            for link in links:
                page_url = locator_domain + link.h3.a["href"]
                street_address = ""
                if link.select_one(".address-line1"):
                    street_address = link.select_one(".address-line1").text.strip()
                if link.select_one(".address-line2"):
                    street_address += (
                        " " + link.select_one(".address-line2").text.strip()
                    )

                state = ""
                if link.select_one(".administrative-area"):
                    state = link.select_one(".administrative-area").text.strip()
                yield SgRecord(
                    page_url=page_url,
                    location_name=link.h3.text.strip(),
                    street_address=street_address,
                    city=link.select_one(".locality").text.strip(),
                    state=state,
                    zip_postal=link.select_one(".postal-code").text.strip(),
                    country_code=link.select_one(".country").text.strip(),
                    phone=link.select_one(".phone-wrapper").text.strip(),
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
