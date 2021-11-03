from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from lxml import html
from sglogging import SgLogSetup

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

logger = SgLogSetup().get_logger("tacohouse.org")


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
    locator_domain = "https://tacohouse.org/"
    base_url = "https://tacohouse.org/locations-hours/"
    with SgRequests() as session:
        soup = html.fromstring(session.get(base_url, headers=_headers).text)
        locations = soup.xpath(
            '//section[2]//div[contains(@class, "elementor-column elementor-col-50")]'
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            if not _.xpath(".//a/span/span/text()"):
                continue
            address = _.xpath('.//div[contains(@class, "elementor-element")][4]')[
                0
            ].xpath(".//p[1]//text()")
            yield SgRecord(
                page_url=base_url,
                location_name=_.xpath(".//h3/text()")[0],
                street_address=address[0],
                city=address[-1].split(",")[0].strip(),
                state=address[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=address[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=_.xpath('.//div[contains(@class, "elementor-element")][4]')[
                    0
                ].xpath(".//p[2]/strong/text()")[0],
                locator_domain=locator_domain,
                hours_of_operation=_valid(
                    "; ".join(
                        [
                            hh
                            for hh in _.xpath(
                                './/div[contains(@class, "elementor-element")][2]'
                            )[0].xpath(".//text()")
                            if hh.strip()
                        ]
                    )
                ),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
