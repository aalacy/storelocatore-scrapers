from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog


from sgrequests import SgRequests


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://firedpie.com/wp-admin/admin-ajax.php"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    data = "action=get_stores&lat=33.4841196&lng=-112.0749168&radius=5000"

    session = SgRequests()
    son = session.post(url, headers=headers, data=data).json()

    for i in list(son):
        yield son[i]

    logzilla.info(f"Finished grabbing data!!")  # noqa


def human_hours(k):
    days = [
        "Monday: ",
        "Tuesday: ",
        "Wednesday: ",
        "Thursday: ",
        "Friday: ",
        "Saturday: ",
        "Sunday: ",
    ]
    dayIter = 0
    h = []
    for i in list(k):
        if int(i) % 2 == 0:
            h.append(str(days[dayIter] + k[i] + " - "))
            dayIter += 1
        else:
            h.append(str(k[i] + "; "))
    return "".join(h)


def scrape():
    url = "https://firedpie.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["gu"],
        ),
        location_name=sp.MappingField(
            mapping=["na"],
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
        ),
        street_address=sp.MappingField(
            mapping=["st"],
        ),
        city=sp.MappingField(
            mapping=["ct"],
        ),
        state=sp.MissingField(),
        zipcode=sp.MappingField(
            mapping=["zp"],
        ),
        country_code=sp.MissingField(),
        phone=sp.MappingField(
            mapping=["te"],
        ),
        store_number=sp.MappingField(
            mapping=["ID"],
        ),
        hours_of_operation=sp.MappingField(
            mapping=["op"], raw_value_transform=human_hours
        ),
        location_type=sp.MissingField(),
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
