from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog


from sgrequests import SgRequests


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://strackandvantil.com/wp-admin/admin-ajax.php?action=csl_ajax_search&address=no+address+entered&formdata=nameSearch%3D%26addressInputCity%3D%26city_selector_discrete%3D1%26addressInputState%3D%26addressInputCountry%3D%26ignore_radius%3D0&lat=41.30368566585095&lng=-87.28683&options%5Baddress_autocomplete%5D=zipcode&options%5Bappend_to_search%5D=&options%5Bdisable_initial_directory%5D=0&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=base&options%5Bgoogle_map_style%5D=&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=0&options%5Binitial_radius%5D=&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax&options%5Blabel_phone%5D=Phone&options%5Blabel_website%5D=Website&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=Indiana&options%5Bmap_center_lat%5D=40.2671941&options%5Bmap_center_lng%5D=-86.1349019&options%5Bmap_domain%5D=maps.google.com&options%5Bmap_end_icon%5D=https%3A%2F%2Fstrackandvantil.com%2Fwp-content%2Fuploads%2F2018%2F06%2Fmap-pin.png&options%5Bmap_home_icon%5D=https%3A%2F%2Fstrackandvantil.com%2Fwp-content%2Fuploads%2F2017%2F10%2Fhome-map-pin.png&options%5Bmap_region%5D=us&options%5Bmap_type%5D=roadmap&options%5Bno_autozoom%5D=0&options%5Bno_homeicon_at_start%5D=1&options%5Bselector_behavior%5D=either_or&options%5Buse_sensor%5D=false&options%5Bzoom_level%5D=12&options%5Bzoom_tweak%5D=0&radius=5000"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers).json()
    for i in son["response"]:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    try:
        h = []
        for i in x.split(","):
            if len(i) > 3:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def scrape():
    url = "https://strackandvantil.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["url"], value_transform=lambda x: "https://strackandvantil.com" + x
        ),
        location_name=sp.MappingField(mapping=["name"]),
        latitude=sp.MappingField(
            mapping=["lat"],
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
        ),
        street_address=sp.MultiMappingField(
            mapping=[["address"], ["address2"]], value_transform=fix_comma
        ),
        city=sp.MappingField(mapping=["city"]),
        state=sp.MappingField(mapping=["state"]),
        zipcode=sp.MappingField(mapping=["zip"]),
        country_code=sp.MappingField(mapping=["country"], is_required=False),
        phone=sp.MappingField(mapping=["phone"]),
        store_number=sp.MappingField(mapping=["id"]),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
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
