from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
import json


DOMAIN = "allenedmonds.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
MISSING = "<MISSING>"

url = "https://platform.cloud.coveo.com/rest/search/v2?sitecoreItemUri=sitecore%3A%2F%2Fweb%2F%7BBC36F0B1-242B-47E7-8D4C-E7DCF3F76D63%7D%3Flang%3Den%26amp%3Bver%3D1&siteName=Allen%20Edmonds"

payload = "actionsHistory=%5B%5D&referrer=&visitorId=2ff95bbd-90b7-d05a-4668-7f78f2755169&isGuestUser=false&aq=(%24qf(function%3A'dist(%40latitude%2C%20%40longitude%2C%2038.912%2C%20-80.019)'%2C%20fieldName%3A%20'distance'))%20(%40distance%3C%3D1000000000)&cq=%40source%3D%3D39099_AllenEdmonds_Catalog&searchHub=AllenEdmondsStoreLocator&locale=en&maximumAge=900000&firstResult=0&numberOfResults=5000&excerptLength=2000"
headers = {
    "authority": "platform.cloud.coveo.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer xx6b22c1da-b9c6-495b-9ae1-e3ac72612c6f",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.allenedmonds.com",
    "referer": "https://www.allenedmonds.com/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
}


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_JSON_object_variable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def hoo(hoos):
    sundayhours = get_JSON_object_variable(hoos, "sundayhours")
    wednesdayhours = get_JSON_object_variable(hoos, "wednesdayhours")
    mondayhours = get_JSON_object_variable(hoos, "mondayhours")
    thursdayhours = get_JSON_object_variable(hoos, "thursdayhours")
    saturdayhours = get_JSON_object_variable(hoos, "saturdayhours")
    tuesdayhours = get_JSON_object_variable(hoos, "tuesdayhours")
    fridayhours = get_JSON_object_variable(hoos, "fridayhours")

    hs = f"Sun: {sundayhours}; Mon: {mondayhours}; Tue: {tuesdayhours}; Wed: {wednesdayhours}; Thu: {thursdayhours}; Fri: {fridayhours}; Sat: {saturdayhours}"

    return hs


def parse_json(details):
    data = {}
    data["locator_domain"] = DOMAIN
    data["location_name"] = get_JSON_object_variable(details, "systitle")

    data["store_number"] = get_JSON_object_variable(details, "storeid")

    data["page_url"] = get_JSON_object_variable(details, "sysuri")
    data["location_type"] = get_JSON_object_variable(details, "objecttype")
    data["street_address"] = (
        get_JSON_object_variable(details, "address1")
        + ","
        + get_JSON_object_variable(details, "address2")
    )
    data["street_address"] = data["street_address"].replace(",<MISSING>", "")
    data["city"] = get_JSON_object_variable(details, "city")
    data["state"] = get_JSON_object_variable(details, "state")
    data["country_code"] = get_JSON_object_variable(details, "country")
    data["zip_postal"] = get_JSON_object_variable(details, "formattedzipcode")
    data["phone"] = get_JSON_object_variable(details, "formattedphonenumber")
    data["latitude"] = get_JSON_object_variable(details, "latitude")
    data["longitude"] = get_JSON_object_variable(details, "longitude")
    data["raw_address"] = MISSING
    data["hours_of_operation"] = hoo(details)

    return data


def fetch_data():
    with SgRequests() as session:

        response = session.post(url, headers=headers, data=payload)
        logger.info(f"Response: {response}")

        locations = json.loads(response.text)["results"]
        logger.info(f"Total Stores: {len(locations)}")
        for location in locations:
            details = location["raw"]
            if location["raw"]["systitle"] == "ONLINE":
                continue
            i = parse_json(details)
            yield i


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(DOMAIN),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
        street_address=sp.MappingField(mapping=["street_address"], is_required=False),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zip_postal"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["store_number"], is_required=False),
        hours_of_operation=sp.MappingField(
            mapping=["hours_of_operation"], is_required=False
        ),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
