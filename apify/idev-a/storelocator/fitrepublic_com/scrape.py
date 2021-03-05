from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
import sglogging
from bs4 import BeautifulSoup as bs

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://fitrepublic.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}

log = sglogging.SgLogSetup().get_logger(
    logger_name="fitrepublic.com", stdout_log_level="INFO"
)


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
        locator_domain = "https://fitrepublic.com/"
        base_url = "https://api2.storepoint.co/v1/15c06d849dfcc8/locations?lat=34.0485&long=-118.2529&radius=500"
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["results"]["locations"]:
            addr = parse_address_intl(_["streetaddress"])
            hours_of_operation = ""
            try:
                if _["website"]:
                    r1 = session.get(_["website"], headers=_headers)
                    soup1 = bs(r1.text, "lxml")
                    horizontal_rule = soup1.select("div.sqs-block-horizontalrule")[0]
                    hours_of_operation = "; ".join(
                        [_ for _ in horizontal_rule.next_sibling.stripped_strings][1:]
                    )
            except Exception as err:
                import pdb

                pdb.set_trace()
                log.info(str(err))
            yield SgRecord(
                page_url=_["website"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                latitude=_["loc_lat"],
                longitude=_["loc_long"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=_valid(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
