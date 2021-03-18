from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from lxml import html

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}

log = SgLogSetup().get_logger(logger_name="ccfoodmarts.com")


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "http://www.ccfoodmarts.com/"
        base_url = "http://www.ccfoodmarts.com/locations.php"
        soup = html.fromstring(session.get(base_url, headers=_headers).text)
        links = soup.xpath("//map/area")
        for link in links:
            page_url = locator_domain + link.xpath("./@href")[0]
            soup1 = html.fromstring(session.get(page_url, headers=_headers).text)
            blocks = soup1.xpath("//table//table//table//tr[4]/td//text()")
            log.info(page_url)
            yield SgRecord(
                page_url=page_url,
                location_name=soup1.xpath("//h3/text()")[0],
                street_address=" ".join(blocks[:-3]),
                city=blocks[-2].split(",")[0].strip(),
                state=blocks[-2].split(",")[1].strip().split(" ")[0],
                zip_postal=blocks[-2].split(",")[1].strip().split(" ")[1],
                country_code="US",
                phone=blocks[-1].strip(),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
