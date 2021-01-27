from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sglogging import sglog


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")

    url = "https://www.peugeot.co.uk/api/search-pointofsale/en/1/GB/1/100000/100000/100000/10000/10000/10000/1?departure=0.0%2C0.0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers).json()

    # noqa this was not needed :son = getjson(url,headers)

    for i in son["listDealer"]:
        try:
            i["schedules"] = i["schedules"]
        except Exception:
            i["schedules"] = ""
        yield i
    for i in son["new_vehicle_dealers"]:
        try:
            i["schedules"] = i["schedules"]
        except Exception:
            i["schedules"] = ""
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        x = x.split("-")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def nice_hours(k):
    return k.replace("<br />", "; ")


def scrape():
    url = "https://www.peugeot.co.uk/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["contact", "website"],
            is_required=False,
        ),
        location_name=sp.MappingField(mapping=["name"], is_required=False),
        latitude=sp.MappingField(
            mapping=["adress", "lat"],
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["adress", "lng"],
            is_required=False,
        ),
        street_address=sp.MappingField(
            mapping=["adress", "street"],
            is_required=False,
            value_transform=fix_comma,
        ),
        city=sp.MappingField(mapping=["adress", "dealer_city"], is_required=False),
        state=sp.MappingField(
            mapping=["adress", "region"],
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["adress", "zip_code"],
            is_required=False,
        ),
        country_code=sp.MappingField(mapping=["adress", "country"]),
        phone=sp.MappingField(
            mapping=["contact", "tel"],
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["id"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["schedules"], is_required=False, value_transform=nice_hours
        ),
        location_type=sp.MappingField(mapping=["type"]),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
