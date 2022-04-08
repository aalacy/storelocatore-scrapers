from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import CrawlStateSingleton


logger = SgLogSetup().get_logger("cellularsales_com")


def write_output(data):
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)


def fetch_data(http: SgRequests, search: DynamicGeoSearch):
    # Your scraper here

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    }
    state = CrawlStateSingleton.get_instance()
    for lati, longi in search:
        rec_count = state.get_misc_value(
            search.current_country(), default_factory=lambda: 0
        )
        state.set_misc_value(search.current_country(), rec_count + 1)

        url = (
            "https://www.cellularsales.com/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(lati)
            + "&lng="
            + str(longi)
            + "&max_results=25&search_radius=500&autoload=1"
        )
        logger.info(url)
        r = http.get(url, headers=headers)
        try:
            allocs = r.json()
        except:
            continue
        if allocs:
            search.found_location_at(lati, longi)

        for al in allocs:

            zip = al["zip"].split("-")[0].strip()
            if len(zip) == 4:
                zip = "0" + zip

            try:
                tim = (
                    al["hours"]
                    .split('class="wpsl-opening-hours">')[1]
                    .replace("</time></td></tr>", " ")
                    .replace("</td><td><time>", " ")
                    .replace("</table>", "")
                    .replace("<tr><td>", " ")
                    .replace("</td></tr>", " ")
                    .replace("</td><td>", " ")
                    .strip()
                )
            except:
                tim = "<MISSING>"

            yield SgRecord(
                locator_domain="https://www.cellularsales.com",
                page_url=al["permalink"],
                location_name=al["store"],
                street_address=al["address"] + " " + al["address2"].strip(),
                city=al["city"],
                state=al["state"],
                zip_postal=zip,
                country_code="US",
                store_number=al["id"],
                phone=al["phone"],
                location_type="<MISSING>",
                latitude=al["lat"],
                longitude=al["lng"],
                hours_of_operation=tim,
            )


def scrape():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=500,
        max_search_results=25,
    )
    with SgRequests() as http:
        data = fetch_data(http, search)
    write_output(data)

    state = CrawlStateSingleton.get_instance()
    logger.info(state.get_misc_value("us", default_factory=lambda: 0))


scrape()
