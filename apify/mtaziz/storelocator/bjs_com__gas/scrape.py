from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup
from sgrequests import SgRequests

logger = SgLogSetup().get_logger(logger_name="bjs_com__gas")
session = SgRequests()

locator_domain = "https://www.bjs.com"


def fetch_data():

    city_data = session.get(
        "https://api.bjs.com/digital/live/apis/v1.0/clublocatorpage/statetowns/10201"
    ).json()

    for town in city_data["clubLocatorStateTownList"]:
        for number in town["Towns"]:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
            }
            town_number = number.split("|")[0]
            town_name = number.split("|")[1]
            logger.info(f"[Town Number:{town_number}:{town_name}]")
            slug = number.split("|")[1].replace(" ", "-").replace(",", "").lower()
            logger.info(f"[Slug:{slug}]")
            url = "https://api.bjs.com/digital/live/api/v1.0/club/search/10201"
            payload = (
                '{"Town":"'
                + str(town_number)
                + '","latitude":"","longitude":"","radius":"","zipCode":""}'
            )
            logger.info(f"[Payload Formed:{payload}]")

            json_data = session.post(url, data=payload, headers=headers).json()
            logger.info(f"[Crawling the data for the town:{town_name}]")
            for _ in json_data["Stores"]["PhysicalStore"]:
                hours = ""
                for attr in _["Attribute"]:
                    if attr["name"] == "Gas Hours":
                        hours = attr["displayValue"].replace("<br>", " ")
                if hours == "":
                    continue
                page_url = (
                    "https://www.bjs.com/cl/" + str(slug) + "/" + str(town_number)
                )

                yield SgRecord(
                    page_url=page_url,
                    location_name="BJ'S WHOLESALE CLUB AT"
                    + _["Description"][0]["displayStoreName"],
                    street_address=" ".join(_["addressLine"]).strip("."),
                    city=_["city"],
                    state=_["stateOrProvinceName"],
                    zip_postal=_["postalCode"],
                    store_number=_["uniqueID"],
                    location_type="GAS",
                    country_code="US",
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    phone=_["telephone1"],
                    locator_domain=locator_domain,
                    hours_of_operation=hours,
                )
    logger.info("Scraping Finished")


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
