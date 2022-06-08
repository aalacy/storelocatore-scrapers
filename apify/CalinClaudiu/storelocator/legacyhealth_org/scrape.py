from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests


logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def fetch_data():

    url = (
        "https://www.legacyhealth.org/featureapi/v1/location-and-providersearch/search"
    )
    headers = {}
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"
    headers["X-Requested-With"] = "XMLHttpRequest"
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    PageNumber = 1

    with SgRequests(verify_ssl=False) as session:
        locs = SgRequests.raise_on_err(
            session.post(
                url,
                headers=headers,
                data=f"Latitude=&Longitude=&keyword=&services=&ActiveLocationTypeFilter=&ZipCode=&Radius=50000&PageNumber={PageNumber}&SearchType=LOCATIONS&Specialties=&Locations=&OpenWeekends=false&Open24Hours=false",
            )
        ).json()
        for record in locs["JsonLocations"]:
            yield record
        PageNumber += 1
        while PageNumber <= locs["PageCount"]:
            locs = SgRequests.raise_on_err(
                session.post(
                    url,
                    headers=headers,
                    data=f"Latitude=&Longitude=&keyword=&services=&ActiveLocationTypeFilter=&ZipCode=&Radius=50000&PageNumber={PageNumber}&SearchType=LOCATIONS&Specialties=&Locations=&OpenWeekends=false&Open24Hours=false",
                )
            ).json()
            for record in locs["JsonLocations"]:
                yield record
            PageNumber += 1

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    cop = []
    try:
        for i in x:
            if i:
                cop.append(i)
        x = ", ".join(cop)
    except Exception as e:
        logzilla.error(f"{x}", exc_info=e)

    try:
        x = x.replace("None", "")
        x = x.split(",")
        copy = []
        for i in x:
            if len(i.strip()) > 0:
                copy.append(i.strip())
        x = ", ".join(copy)
        return x
    except Exception as e:
        logzilla.error(f"{x}", exc_info=e)
        return x.replace("None", "")


def scrape():
    url = "https://www.gohealthuc.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["Url"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["Title"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        latitude=sp.MappingField(
            mapping=["Latitude"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["Longitude"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        street_address=sp.MultiMappingField(
            mapping=[
                ["Address1"],
                ["Address2"],
            ],
            part_of_record_identity=True,
            raw_value_transform=fix_comma,
            is_required=False,
        ),
        city=sp.MappingField(
            mapping=["City"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        state=sp.MappingField(
            mapping=["State"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["Zip"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=sp.MissingField(),
        phone=sp.MappingField(
            mapping=["Phone"],
            value_transform=lambda x: x.replace("None", "<MISSING>")
            .replace("Phone:", "")
            .strip(),
            is_required=False,
        ),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MappingField(
            mapping=["PracticeOfficeHours"],
            is_required=False,
        ),
        location_type=sp.MappingField(
            mapping=["LocationType", "Title"],
            value_transform=lambda x: x.split("/", 1)[0],
        ),
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
