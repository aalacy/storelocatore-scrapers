from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog


def determine(banner, ide):
    link = {
        "independentcitymarket": "https://www.independentcitymarket.ca/",
        "superstore": "https://realcanadiansuperstore.ca/",
        "provigo": "https://provigo.ca/",
        "valumart": "https://valumart.ca/",
        "nofrills": "https://nofrills.ca/",
        "independent": "https://yourindependentgrocer.ca/",
        "rass": "https://atlanticsuperstore.ca/",
        "loblaw": "https://www.loblaws.ca/",
        "dominion": "https://joefresh.com/",
        "zehrs": "https://www.zehrs.ca/",
        "extrafoods": "https://www.extrafoods.ca/",
        "fortinos": "https://www.fortinos.ca/",
        "maxi": "https://maxi.ca/",
        "wholesaleclub": "https://www.wholesaleclub.ca/",
    }
    return link[banner], link[banner] + "store-locator/details/" + ide


def para(k):
    session = SgRequests()
    ban = k["storeBannerId"]
    ide = k["id"]
    backup = k
    backupPhone = k["contactNumber"]
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Site-Banner": ban,
    }
    try:
        k = session.get(
            "https://www.loblaws.ca/api/pickup-locations/" + k["id"],
            headers=headers,
        ).json()
    except Exception:
        try:
            k = session.get(
                "https://www.loblaws.ca/api/pickup-locations/" + k["StoreId"],
                headers=headers,
            ).json()
        except Exception:
            k = backup
            k["hours"] = k["openNowResponseData"]["hours"]
            k["storeDetails"] = {}
            k["storeDetails"]["phoneNumber"] = backupPhone

    try:
        k["hours"] = "; ".join(
            [str(i["day"] + ": " + i["hours"]) for i in k["storeDetails"]["storeHours"]]
        )
    except:
        k = backup
        k["hours"] = k["openNowResponseData"]["hours"]
        k["storeDetails"] = {}
        k["storeDetails"]["phoneNumber"] = k["contactNumber"]
    k["domain"], k["page_url"] = determine(ban, ide)
    k["storeBannerId"] = ban
    k["storeId"] = ide
    if not k["storeDetails"]["phoneNumber"]:
        k["storeDetails"]["phoneNumber"] = backupPhone

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")  # noqa
    url = "https://www.loblaws.ca/api/pickup-locations?"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers).json()
    # I already have 99% of data, however some stores don't have their phone numbers in this main json. Must make individual requests.
    # sub-request https://www.loblaws.ca/api/pickup-locations/3957
    # only important header example : Site-Banner: nofrills
    # banners = {'independentcitymarket', 'superstore', 'provigo', 'valumart', 'nofrills', 'independent', 'rass', 'loblaw', 'dominion',
    # noqa #'zehrs', 'extrafoods', 'fortinos', 'maxi', 'wholesaleclub'}

    lize = utils.parallelize(
        search_space=son,
        fetch_results_for_rec=para,
        max_threads=20,
        print_stats_interval=20,
    )
    for i in lize:
        yield i


def fix_comma(x):
    h = []

    x = x.replace("None", "")
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1 or any(char.isdigit() for char in i):
                h.append(i)
        h = ", ".join(h)
    except:
        h = x

    if len(h) < 2:
        h = "<MISSING>"

    if "MFC HIGH TECH" in h:
        h = fix_comma(h.replace("MFC HIGH TECH", "").strip())

    if "MORRISBURG SHOPPING PLAZA" in h:
        h = fix_comma(h.replace("MORRISBURG SHOPPING PLAZA", "").strip())

    if "MFC SCARBOROUGH" in h:
        h = fix_comma(h.replace("MFC SCARBOROUGH", "").strip())

    if "MFC MCCOWAN" in h:
        h = fix_comma(h.replace("MFC MCCOWAN", "").strip())

    if "MFC GLEN ERIN" in h:
        h = fix_comma(h.replace("MFC GLEN ERIN", "").strip())

    if "Morrisburg Shopping Plaza" in h:
        h = fix_comma(h.replace("Morrisburg Shopping Plaza", "").strip())

    if "MFC Glen Erin" in h:
        h = fix_comma(h.replace("MFC Glen Erin", "").strip())

    if "MFC High Tech" in h:
        h = fix_comma(h.replace("MFC High Tech", "").strip())

    if "Pearlgate Plaza" in h:
        h = fix_comma(h.replace("Pearlgate Plaza", "").strip())

    if "MFC Scarborough" in h:
        h = fix_comma(h.replace("MFC Scarborough", "").strip())

    if "MFC McCowan" in h:
        h = fix_comma(h.replace("MFC McCowan", "").strip())

    return h.strip()


def scrape():
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=MappingField(mapping=["domain"]),
        page_url=MappingField(mapping=["page_url"]),
        location_name=MappingField(mapping=["name"]),
        latitude=MappingField(mapping=["geoPoint", "latitude"]),
        longitude=MappingField(mapping=["geoPoint", "longitude"]),
        street_address=MultiMappingField(
            mapping=[["address", "line1"], ["address", "line2"]],
            part_of_record_identity=True,
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=MappingField(
            mapping=["address", "town"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            part_of_record_identity=True,
        ),
        state=MappingField(
            mapping=["address", "region"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            part_of_record_identity=True,
        ),
        zipcode=MappingField(
            mapping=["address", "postalCode"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MappingField(
            mapping=["address", "country"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        phone=MappingField(
            mapping=["storeDetails", "phoneNumber"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        store_number=MappingField(mapping=["storeId"]),
        hours_of_operation=MappingField(
            mapping=["hours"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        location_type=MappingField(
            mapping=["storeBannerId"], part_of_record_identity=True
        ),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="Loblaws Family",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
