from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}

logger = SgLogSetup().get_logger("washnfillstores.com")


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


def _phone(_):
    return _.select("li")[4].text.replace("Phone:", "").strip()


def fetch_data():
    with SgRequests() as session:
        locator_domain = "http://washnfillstores.com/"
        base_url = "http://washnfillstores.com/location.html"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.locColumns")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            coord = _.iframe.a["href"].split("&ll=")[1].split("&s")[0].split(",")
            yield SgRecord(
                page_url=base_url,
                location_name=_.h4.text.strip(),
                street_address=_.select("li")[2].text,
                city=_.select("li")[3].text.split(",")[0].strip(),
                state=_.select("li")[3].text.split(",")[1].strip().split(" ")[0],
                zip_postal=_.select("li")[3].text.split(",")[1].strip().split(" ")[-1],
                country_code="US",
                phone=_phone(_),
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
