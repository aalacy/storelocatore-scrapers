from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests
import ssl
import json

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def fix_record2(rec):
    country = rec[1]
    rec = rec[0]
    k = {}
    k["host"] = "<MISSING>"

    try:
        k["name"] = rec["storeDisplayName"]
    except Exception:
        k["name"] = "<MISSING>"

    k["latitude"] = "<MISSING>"

    k["longitude"] = "<MISSING>"

    try:
        k["address"] = rec["address"]["addrLine1"]
        try:
            k["address"] = k["address"] + rec["address"]["addrLine2"]
        except Exception:
            pass
    except Exception:
        k["address"] = "<MISSING>"

    k["state"] = "<MISSING>"
    k["zip"] = "<MISSING>"

    try:
        k["city"] = rec["address"]["city"]
    except Exception:
        k["city"] = "<MISSING>"

    k["country"] = country
    k["id"] = "<MISSING>"
    k["hours"] = "<MISSING>"
    return k


def fix_record(rec, host):
    k = {}

    try:
        k["page_url"] = host + "/" + rec["storeIdentifier"]
    except Exception:
        k["page_url"] = "<MISSING>"
    try:
        k["host"] = host
    except Exception:
        k["host"] = "<MISSING>"

    try:
        k["name"] = rec["storeName"]
    except Exception:
        k["name"] = "<MISSING>"

    try:
        k["latitude"] = rec["latitude"]
    except Exception:
        k["latitude"] = "<MISSING>"

    try:
        k["longitude"] = rec["longitude"]
    except Exception:
        k["longitude"] = "<MISSING>"

    try:
        k["address"] = rec["address"]["addrLine1"]
        try:
            k["address"] = k["address"] + rec["address"]["addrLine2"]
        except Exception:
            pass
    except Exception:
        k["address"] = "<MISSING>"

    try:
        k["state"] = rec["address"]["stateProvince"]
    except Exception:
        k["state"] = "<MISSING>"

    try:
        k["zip"] = rec["address"]["postalCode"]
    except Exception:
        k["zip"] = "<MISSING>"

    try:
        k["city"] = rec["address"]["city"]
    except Exception:
        k["city"] = "<MISSING>"

    try:
        k["country"] = rec["address"]["countryCode"]
    except Exception:
        k["country"] = "<MISSING>"

    try:
        k["id"] = rec["storeNumber"]
    except Exception:
        k["id"] = "<MISSING>"

    try:
        temphr = []
        for day in rec["storeHours"]:
            try:
                if "rue" in day["closed"]:
                    temphr.append(str(day["rolledDays"] + ": Closed"))
            except Exception:
                pass

            try:
                temphr.append(str(day["rolledDays"] + ": " + day["rolledHours"]))
            except Exception:
                pass

        k["hours"] = "; ".join(temphr)
    except Exception:
        try:
            temphr = []
            for day in list(rec["storeHoursMap"]):
                temphr.append(str(str(day) + ": " + str(rec["storeHoursMap"][day])))
            k["hours"] = "; ".join(temphr)
        except Exception:
            k["hours"] = "<MISSING>"

    try:
        k["type"] = str(rec["conceptCode"]) + " - " + str(rec["storeType"])
    except Exception:
        k["type"] = "<MISSING>"
    return k


def dissect_country(data):
    for country in list(data["statesAndProvinces"]):
        for rec in data["statesAndProvinces"][country]["stores"]:
            yield (rec, country)


def main_all(session, url):

    headers = {}
    headers[
        "accept"
    ] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    headers["accept-encoding"] = "gzip, deflate, br"
    headers["accept-language"] = "en-US,en;q=0.9,ro;q=0.8,es;q=0.7"
    headers["cache-control"] = "no-cache"
    headers["pragma"] = "no-cache"
    headers["referer"] = "http://www.williams-sonomainc.com/"
    headers[
        "sec-ch-ua"
    ] = '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"'
    headers["sec-ch-ua-mobile"] = "?0"
    headers["sec-ch-ua-platform"] = '"Windows"'
    headers["sec-fetch-dest"] = "document"
    headers["sec-fetch-mode"] = "navigate"
    headers["sec-fetch-site"] = "cross-site"
    headers["sec-fetch-user"] = "?1"
    headers["upgrade-insecure-requests"] = "1"
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"

    page = SgRequests.raise_on_err(session.get(url, headers=headers))
    data = page.text

    data = data.split("__INITIAL_STATE__=", 1)[1]
    data = data.split("</script>", 1)[0]
    data = data.rsplit(";(functi", 1)[0]
    data = json.loads(data)
    try:
        host = data["phygital"]["clientApplicationUri"]
    except Exception:
        host = ""
    for country in list(data["phygital"]["storesList"]):
        for state in list(data["phygital"]["storesList"][country]):
            for record in data["phygital"]["storesList"][country][state]:
                yield fix_record(record, host)
    for country in data["phygital"]["config"]["stores"]["storeLocator"]["countryList"]:
        for item in dissect_country(country):
            yield fix_record2(item)


def fetch_data():
    with SgRequests() as session:

        for item in main_all(
            session, "https://www.potterybarnkids.com/stores/?cm_src=OLDLINK"
        ):
            yield item

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(
            mapping=["host"],
        ),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["name"], is_required=False, part_of_record_identity=True
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["address"], part_of_record_identity=True
        ),
        city=sp.MappingField(
            mapping=["city"], is_required=False, part_of_record_identity=True
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(
            mapping=["country"], is_required=False, part_of_record_identity=True
        ),
        phone=sp.MissingField(),
        store_number=sp.MappingField(
            mapping=["id"],
            is_required=False,
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["type"], is_required=False),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=10,
        duplicate_streak_failure_factor=-1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
