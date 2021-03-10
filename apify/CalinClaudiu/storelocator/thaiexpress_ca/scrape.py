from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


def parse_store(store):
    k = {}
    try:
        crappyaddr = store.find("address").text.strip()
        crappyaddr = crappyaddr.split("  ")
    except Exception:
        crappyaddr = "<MISSING>"

    if len(crappyaddr) > 3:
        if (len(crappyaddr[-1])) < 4:
            crappyaddr[-2] = crappyaddr[-2] + " " + crappyaddr[-1]
            crappyaddr.pop(-1)
        else:
            crappyaddr[1] = crappyaddr[0] + ", " + crappyaddr[1]
            crappyaddr.pop(0)

    try:
        k["Name"] = store.find("location").text.strip()
    except Exception:
        k["Name"] = "<MISSING>"

    try:
        k["Latitude"] = store.find("latitude").text.strip()
    except Exception:
        k["Latitude"] = "<MISSING>"

    try:
        k["Longitude"] = store.find("longitude").text.strip()
    except Exception:
        k["Longitude"] = "<MISSING>"

    try:
        k["Address"] = crappyaddr[0].strip()
        crappyaddr.pop(0)
        while any(i.isdigit() for i in crappyaddr[0]):
            k["Address"] = k["Address"] + ", " + crappyaddr[0].strip()
            crappyaddr.pop(0)
        if len(k["Address"]) < 5:
            k["Address"] = k["Address"] + ", " + crappyaddr[0].strip()
            crappyaddr.pop(0)
        if crappyaddr[0] == "Lapiniere" and k["Address"] == "2151 boulevard":
            k["Address"] = k["Address"] + ", " + crappyaddr[0].strip()
            crappyaddr.pop(0)

    except Exception:
        k["Address"] = "<MISSING>"

    try:
        k["City"] = crappyaddr[0].strip()
        crappyaddr.pop(0)
    except Exception:
        k["City"] = "<MISSING>"

    try:
        k["State"] = crappyaddr[-1].strip()
        k["State"] = k["State"].split(" ")[0]
    except Exception:
        k["State"] = "<MISSING>"

    try:
        k["Zip"] = crappyaddr[-1].strip()
        k["Zip"] = k["Zip"].split(" ")
        k["Zip"].pop(0)
        k["Zip"] = " ".join(k["Zip"])
    except Exception:
        k["Zip"] = "<MISSING>"

    k["CountryCode"] = "<MISSING>"

    try:
        k["Phone"] = store.find("telephone").text.strip()
    except Exception:
        k["Phone"] = "<MISSING>"

    try:
        k["StoreId"] = store.find("storeid").text.strip()
    except Exception:
        k["StoreId"] = "<MISSING>"

    try:
        hours = store.find("operatinghours").text.strip()
        hours = "<div>" + hours + "</div>"
        hours = b4(hours, "lxml")
        hours = list(hours.stripped_strings)
        k["hours"] = "; ".join(hours).replace("&nbsp;", " ")
    except Exception:
        k["hours"] = "<MISSING>"

    try:
        hours = store.find("description").text.strip()
        hours = "<div>" + hours + "</div>"
        hours = b4(hours, "lxml")
        hours = list(hours.stripped_strings)
        k["StatusName"] = "/".join(hours).replace("&nbsp;", " ")
    except Exception:
        k["StatusName"] = "<MISSING>"

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://thaiexpress.ca/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    stores = soup.find("store")
    stores = stores.find_all("item")
    for i in stores:
        k = parse_store(i)
        if "Closed permanently" in k["hours"]:
            k["StatusName"] = k["StatusName"] + "/Closed permanently"
        yield k

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    x.replace("None", "<MISSING>")
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1:
                h.append(i)
        h = ", ".join(h)
    except Exception:
        h = x

    return h.replace("&#39;", "'").replace("&#44;", ",").replace(",,", ",")


def clean_hours(x):

    try:
        x = x.split(">")[1]
        x = x.split("<")[0]
        if len(x) < 3:
            return "<MISSING>"
        try:
            x = x.split("you;")[1]
        except Exception:
            x = x

        return (
            x.replace("day", "day:")
            .replace("::", ":")
            .replace("\n", "; ")
            .replace("\r", "; ")
            .replace(": ;", ": Closed;")
            .replace("&nbsp;", " ")
            .replace("Â", " ")
            .replace(";;", ";")
            .replace("Temporairement fermé;", "")
            .replace("Temporarily closed;", "")
        ).strip()

    except Exception:
        try:
            x = x.split("you;")[1]
        except Exception:
            x = x
        return (
            x.replace("day", "day:")
            .replace("::", ":")
            .replace("\n", "; ")
            .replace("\r", "; ")
            .replace(": ;", ": Closed;")
            .replace("&nbsp;", " ")
            .replace("Â", " ")
            .replace(";;", ";")
            .replace("Temporairement fermé;", "")
            .replace("Temporarily closed;", "")
        ).strip()


def scrape():
    url = "https://www.thaiexpress.ca/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MissingField(),
        location_name=MappingField(
            mapping=["Name"],
            is_required=False,
            part_of_record_identity=True,
            value_transform=lambda x: x.replace("&#39;", "'").replace(",,", ","),
        ),
        latitude=MappingField(mapping=["Latitude"]),
        longitude=MappingField(mapping=["Longitude"]),
        street_address=MappingField(
            mapping=["Address"],
            value_transform=fix_comma,
            part_of_record_identity=True,
        ),
        city=MappingField(
            mapping=["City"],
            is_required=False,
            value_transform=fix_comma,
            part_of_record_identity=True,
        ),
        state=MappingField(
            mapping=["State"],
            is_required=False,
            value_transform=fix_comma,
            part_of_record_identity=True,
        ),
        zipcode=MappingField(
            mapping=["Zip"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MappingField(mapping=["CountryCode"]),
        phone=MappingField(
            mapping=["Phone"],
            value_transform=lambda x: x.replace("() -", "<MISSING>"),
            is_required=False,
        ),
        store_number=MappingField(mapping=["StoreId"]),
        hours_of_operation=MappingField(
            mapping=["hours"], is_required=False, value_transform=clean_hours
        ),
        location_type=MappingField(
            mapping=["StatusName"],
            is_required=False,
            part_of_record_identity=True,
        ),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="pinkberry.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
        post_process_filter=lambda x: "Closed permanently" not in x.location_type(),
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
