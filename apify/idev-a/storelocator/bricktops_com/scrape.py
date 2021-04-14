from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bricktops")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://bricktops.com"
    base_url = "https://bricktops.com/locations"
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("div.sqs-gallery a")
        for link in links:
            page_url = link["href"] + "/contact"
            if not link["href"].startswith("https"):
                page_url = locator_domain + link["href"]
            logger.info(page_url)
            driver.get(page_url)
            sp1 = bs(driver.page_source, "lxml")
            addr = None
            hours_of_operation = ""
            phone = ""
            if not link["href"].startswith("https"):
                location_name = sp1.select_one(".sqs-block-content h1").text
                phone = sp1.select("div.sqs-block-html div.sqs-block-content")[
                    -1
                ].h3.text
                hours_of_operation = "; ".join(
                    [
                        _.text
                        for _ in sp1.select("div.sqs-block-html div.sqs-block-content")[
                            -1
                        ].select("p")[1:-1]
                    ]
                ).replace("–", "-")
                addr = list(
                    sp1.select("div.sqs-block-html div.sqs-block-content")[-1]
                    .select("p")[-1]
                    .stripped_strings
                )
            else:
                addr = list(
                    sp1.select("div.sqs-block-html div.sqs-block-content")[0]
                    .select("p")[-1]
                    .stripped_strings
                )
                location_name = link.img["alt"].replace(".png", "")
            city = state = zip_postal = ""
            try:
                city = addr[1].split(",")[0].strip()
                state = addr[1].split(",")[1].strip().split(" ")[0].strip()
                zip_postal = addr[1].split(",")[1].strip().split(" ")[-1].strip()
            except:
                city = ""
                pass
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=addr[0],
                city=city,
                state=state,
                zip_postal=zip_postal,
                phone=phone,
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
