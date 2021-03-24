from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog


from sgrequests import SgRequests


def decimate(bboxes):
    # making one big bbox into smaller quadrants until I no longer get 1000 results per query.
    new_bboxes = []
    for i in bboxes:
        centLng = (i["lng1"] + i["lng2"]) / 2
        centLat = (i["lat1"] + i["lat2"]) / 2
        bbox0 = {
            "lng1": i["lng1"],
            "lng2": centLng,
            "lat1": i["lat1"],
            "lat2": centLat,
        }  # minLon, centLng, minLat, centLat
        bbox1 = {
            "lng1": centLng,
            "lng2": i["lng2"],
            "lat1": i["lat1"],
            "lat2": centLat,
        }  # centLng, maxLon, minLat, centLat
        bbox2 = {
            "lng1": i["lng1"],
            "lng2": centLng,
            "lat1": centLat,
            "lat2": i["lat2"],
        }  # minLon, centLng, centLat, maxLat
        bbox3 = {
            "lng1": centLng,
            "lng2": i["lng2"],
            "lat1": centLat,
            "lat2": i["lat2"],
        }  # centLng, maxLon, centLat, maxLat
        new_bboxes.append(bbox0)
        new_bboxes.append(bbox1)
        new_bboxes.append(bbox2)
        new_bboxes.append(bbox3)
    bboxes = new_bboxes
    # decimate above tests below
    url = "https://stores.shoppersdrugmart.ca/umbraco/api/location/GetNearestLocations?lat1={lat1}&lng1={lng1}&lat2={lat2}&lng2={lng2}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()

    allUnder1000 = True
    results = []
    for i in bboxes:
        son = session.get(
            url.format(lat1=i["lat1"], lng1=i["lng1"], lat2=i["lat2"], lng2=i["lng2"]),
            headers=headers,
        ).json()
        results.append(son)
        if len(son) == 1000:
            allUnder1000 = False
            break
    if allUnder1000:
        for i in results:
            for j in i:
                yield j
    else:
        decimate(bboxes)


def human_hours(k):
    hours = []
    for i in list(k):
        if "storeHours" in i:
            day = []
            day.append(k[i]["dayName"] + ": ") if k[i]["dayName"] else day.append(
                k[i]["date"] + ": "
            )
            if k[i]["closed"] == "false":
                if k[i]["is24Hour"] == "false":
                    day.append(k[i]["from"] + " - " + k[i]["to"])
                else:
                    day.append("24/7")
            else:
                day.append("closed")
            hours.append("".join(day))

    return {"humanHours": "; ".join(hours)}


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    lat1 = 7.031250
    lng1 = -178.945313
    lat2 = 83.236426
    lng2 = -5.615986

    bboxes = []
    bboxes.append({"lat1": lat1, "lng1": lng1, "lat2": lat2, "lng2": lng2})

    for i in decimate(bboxes):
        i.update(human_hours(i))
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        for i in x.split("-"):
            if len(i.strip()) >= 1:
                h.append(i)
        return " - ".join(h)
    except Exception:
        return x


def scrape():
    url = "https://stores.shoppersdrugmart.ca/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["locationID"],
            value_transform=lambda x: url + "en/store/" + x + "/",
        ),
        location_name=sp.MultiMappingField(
            mapping=[["locationDisplayName"], ["locationName"]],
            multi_mapping_concat_with=" - ",
            value_transform=fix_comma,
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MappingField(
            mapping=["address"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["province"],
        ),
        zipcode=sp.MappingField(
            mapping=["zipCode"],
        ),
        country_code=sp.MissingField(),
        phone=sp.MappingField(
            mapping=["phoneNumber"],
        ),
        store_number=sp.MappingField(
            mapping=["locationID"],
        ),
        hours_of_operation=sp.MappingField(
            mapping=["humanHours"],
        ),
        location_type=sp.MappingField(
            mapping=["serviceFilters"],
            value_transform=lambda x: x.replace("'", "")
            .replace("[", "")
            .replace("]", ""),
            is_required=False,
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
