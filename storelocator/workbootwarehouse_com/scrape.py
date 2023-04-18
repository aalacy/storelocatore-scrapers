from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("workbootwarehouse")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.workbootwarehouse.com"
    base_url = "https://www.workbootwarehouse.com/contact-us/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.services a.service__link")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(sp1.select("div.entry__content p")[0].a.stripped_strings)
            script = sp1.select("div.marker")[-1]
            hours_of_operation = "; ".join(
                list(
                    sp1.select("div.contact-info__content div.entry__content p")[
                        -1
                    ].stripped_strings
                )[1:]
            ).replace("–", "-")
            if (
                "We are closed on"
                in sp1.select("div.contact-info__content div.entry__content p")[-1].text
            ):
                hours_of_operation = "Temporarily closed"
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("div.entry__content h3").text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=sp1.select("div.entry__content p")[1].a.text.strip(),
                locator_domain=locator_domain,
                latitude=script["data-lat"],
                longitude=script["data-lng"],
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
