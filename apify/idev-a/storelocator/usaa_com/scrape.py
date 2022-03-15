from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("usaa")

_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "wicket-ajax": "true",
    "wicket-ajax-baseurl": "?0&amp;taskCode=ATM&amp;wa_ref=lf_atm",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

_header1 = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _v(val):
    return val.replace("<![CDATA[", "").replace("]]>", "")


def fetch_data():
    locator_domain = "https://www.usaa.com/"
    base_url = "https://www.usaa.com/inet/ent_locationServices/UsaaLocator/?0&taskCode=ATM&wa_ref=lf_atm"
    item_url = "https://www.usaa.com/inet/ent_locationServices/UsaaLocator/?0-4.IBehaviorListener.1-locatorBasePanel-actionsPanel-locatorForm&taskCode=ATM&wa_ref=lf_atm&akredirect=true&method=plotCoordinates&latField=39.5&lngField=-98.35&neLat=54.1078729401785&neLng=-58.359765625&swLat=21.038603613458605&swLng=-138.340234375&taskCode=ATM&isGeolocationActive=false&isOnFirstLoad=true"
    detail_url = "https://www.usaa.com/inet/ent_locationServices/UsaaLocator/?0-4.IBehaviorListener.0-locatorBasePanel-actionsPanel-listViewContainer-infoWindowListView-{}-locationLabelLink&taskCode=ATM&wa_ref=lf_atm&akredirect=true"
    with SgRequests() as session:
        res = session.get(base_url, headers=_header1).text
        soup = bs(res, "lxml")
        _headers["x-csrf-token"] = soup.select('input[name="CSRFToken"]')[-1]["value"]
        sp0 = bs(_v(session.get(item_url, headers=_headers).text), "lxml")
        items = sp0.select("div.listViewContainer div.locationLabelLink")
        logger.info(f"{len(items)} found")
        for item in items:
            logger.info(item["id"])
            store_number = item["id"].replace("siteName", "")
            sp1 = bs(
                _v(session.get(detail_url.format(store_number), headers=_headers).text),
                "lxml",
            )
            add1 = sp1.select_one("div.locationAddress2").text.strip()
            yield SgRecord(
                page_url=base_url,
                store_number=store_number,
                location_name=sp1.select_one("div.resultTitle").text.strip(),
                street_address=sp1.select_one("div.locationAddress1").text.strip(),
                city=add1.split(",")[0].strip(),
                state=add1.split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=add1.split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
