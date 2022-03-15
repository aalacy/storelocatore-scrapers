from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("subaru")

_headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "PHPSESSID=cda7afd67028f02f6e7b16f289ceb7a5; _gcl_au=1.1.1529865331.1608884585; _ga=GA1.3.1331527989.1608884586; _gid=GA1.3.80330707.1608884586; reevoo_sp_ses.27e8=*; _fbp=fb.2.1608884589800.1113088602; _hjid=50b3da01-a2ae-4402-8886-d000c0d32fd4; _hjFirstSeen=1; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; _hjIncludedInSessionSample=1; tms_VisitorID=kqk9p0cexj; tms_wsip=1; __sreff=1608884579794.1608885119221.4; __reff=/ mozilla/5.0 (windows nt 10.0|subaru.co.uk %2F referral %2F / mozilla/5.0 (windows nt 10.0; _tq_id.TV-18908154-1.8472=acd9ffc7332ed0d3.1608884586.0.1608885120..; _gat_UA-4806291-3=1; reevoo_sp_id.27e8=89a387d4-9e0e-4ee7-8ca3-e33ceb6c17a6.1608884588.1.1608885125.1608884588.c45f5a4a-f570-49cf-8321-afa126693430",
    "Referer": "https://subaru.co.uk/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

payload = "action=get_stores_by_name&name=&categories%5B0%5D=&filter%5B161%5D=161"


def fetch_data():
    locator_domain = "https://www.subaru.co.uk/"
    base_url = "https://subaru.co.uk/wp-admin/admin-ajax.php"
    with SgRequests() as session:
        locations = session.post(base_url, headers=_headers, data=payload).json()
        logger.info(f"{len(locations)} found")
        for key, _ in locations.items():
            hours = []
            if "showroom" in _["op"]:
                for day, times in _["op"]["showroom"].items():
                    hours.append(f"{day}: {times['open']}-{times['close']}")

            yield SgRecord(
                page_url=_["we"],
                store_number=_["ID"],
                location_name=_["na"],
                street_address=_["st"],
                city=_["ct"],
                zip_postal=_["zp"],
                country_code="Uk",
                phone=_["te"],
                locator_domain=locator_domain,
                latitude=_["lat"],
                longitude=_["lng"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
