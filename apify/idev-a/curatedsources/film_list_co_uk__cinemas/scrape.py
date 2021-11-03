from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("film.list.co.uk")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://film.list.co.uk"
    base_url = "https://film.list.co.uk/cinemas/page:{}/"
    with SgRequests() as session:
        page = 1
        while True:
            soup = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            pagination = (
                soup.select_one("div.pagination strong")
                .text.strip()
                .replace("Page", "")
                .replace("\xa0", "")
                .strip()
                .split("of")
            )

            links = soup.select("div.main div.placeSummary ")
            logger.info(f"[page {page}]{len(links)} found")
            page += 1
            for link in links:
                page_url = locator_domain + link.a["href"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                street_address = city = state = zip_postal = phone = ""
                if link.select_one("address .street-address"):
                    street_address = (
                        link.select_one("address .street-address")
                        .text.replace("\xa0", " ")
                        .strip()
                    )
                if link.select_one("address .locality"):
                    city = (
                        link.select_one("address .locality")
                        .text.replace("\xa0", " ")
                        .strip()
                    )
                if link.select_one("address .region"):
                    state = (
                        link.select_one("address .region")
                        .text.replace("\xa0", " ")
                        .strip()
                    )
                if link.select_one("address .postal-code"):
                    zip_postal = (
                        link.select_one("address .postal-code")
                        .text.replace("\xa0", " ")
                        .strip()
                    )
                if sp1.select_one("li.tel span.value"):
                    phone = sp1.select_one("li.tel span.value").text.strip()
                try:
                    yield SgRecord(
                        page_url=page_url,
                        location_name=link.h2.text.strip(),
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_postal,
                        country_code="UK",
                        phone=phone,
                        locator_domain=locator_domain,
                        latitude=sp1.select_one("span.latitude span")["title"],
                        longitude=sp1.select_one("span.longitude span")["title"],
                    )
                except:
                    import pdb

                    pdb.set_trace()

            if pagination[0] == pagination[1]:
                break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
