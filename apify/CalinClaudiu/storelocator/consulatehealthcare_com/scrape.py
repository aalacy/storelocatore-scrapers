from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

from sgrequests import SgRequests


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")

    headers = {}
    headers["accept"] = "application/json, text/plain, */*"
    headers["accept-encoding"] = "gzip, deflate, br"
    headers["accept-language"] = "en-US,en;q=0.9,ro;q=0.8"
    headers["authorization"] = "YNDRAXWGIEKBMEAP"
    headers["origin"] = "https://centers.consulatehealthcare.com"
    headers["referer"] = "https://centers.consulatehealthcare.com/"
    headers[
        "sec-ch-ua"
    ] = '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"'
    headers["sec-ch-ua-mobile"] = "?0"
    headers["sec-fetch-dest"] = "empty"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-site"] = "cross-site"
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"

    session = SgRequests()

    url = "https://api.momentfeed.com/v1/analytics/api/llp.json?pageSize=100&page="
    page = 0
    while True:
        page += 1
        data = session.get(url + str(page), headers=headers).json()
        try:
            data["message"] = data["message"]
            break
        except Exception:
            pass
        for i in data:
            yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []

    x = x.replace("None", "")
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 2:
                h.append(i)
        h = ", ".join(h)
    except:
        h = x

    if len(h) < 2:
        h = "<MISSING>"

    return h


def scrape():
    url = "https://consulatehealthcare.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["store_info", "website"]),
        location_name=sp.MappingField(mapping=["store_info", "name"]),
        latitude=sp.MappingField(
            mapping=["store_info", "latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["store_info", "longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=[
                ["store_info", "address"],
                ["store_info", "address_extended"],
                ["store_info", "address_3"],
            ],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=sp.MappingField(mapping=["store_info", "locality"]),
        state=sp.MappingField(mapping=["store_info", "region"]),
        zipcode=sp.MappingField(mapping=["store_info", "postcode"]),
        country_code=sp.MappingField(mapping=["store_info", "country"]),
        phone=sp.MappingField(mapping=["store_info", "phone"]),
        store_number=sp.MappingField(mapping=["momentfeed_venue_id"]),
        hours_of_operation=sp.MappingField(mapping=["store_info", "store_hours"]),
        location_type=sp.MappingField(mapping=["store_info", "brand_name"]),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
