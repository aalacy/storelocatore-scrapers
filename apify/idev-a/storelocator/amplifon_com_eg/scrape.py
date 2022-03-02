from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("amplifon")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.amplifon.com.eg"
base_url = "https://www.amplifon.com.eg/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("footer div.quick-list a")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            locations = sp1.select("div.bodytit div.row")
            for _ in locations:
                raw_address = " ".join(
                    _.select_one("address p").stripped_strings
                ).replace("\n", " ")
                addr = parse_address_intl(raw_address + ", Egypt")
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2

                phone = _.select("address p")[1].text.split(":")[-1]
                hours = " ".join(_.select("address p")[-1].stripped_strings)
                if "Work Hours" not in hours:
                    hours = ""

                try:
                    coord = (
                        _.iframe["src"]
                        .split("!2d")[1]
                        .split("!2m")[0]
                        .split("!3m")[0]
                        .split("!3d")
                    )
                except:
                    coord = ["", ""]

                city = addr.city
                location_name = _.h4.text.strip()
                if not city:
                    city = location_name
                yield SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="Egypt",
                    phone=phone,
                    latitude=coord[1],
                    longitude=coord[0],
                    locator_domain=locator_domain,
                    hours_of_operation=hours.replace("Work Hours:", "").replace(
                        "\n", " "
                    ),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.RAW_ADDRESS})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
