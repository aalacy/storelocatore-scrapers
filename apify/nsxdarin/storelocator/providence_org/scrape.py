from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("providence_org")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    country = "US"
    website = "providence.org"
    typ = "<MISSING>"
    store = "<MISSING>"
    for x in range(1, 150):
        logger.info(x)
        url = (
            "https://providenceapi.azureedge.net/api/kyruusquery?facet=none!&fields=-ALL%2C%2Baccepting_new_patients%2C%2Bage_groups_seen%2C%2Bboard_certifications%2C%2Bdegrees%2C%2Bgender%2C%2Bid%2C%2Bimage_url%2C%2Binsurance_accepted%2C%2Bis_primary_care%2C%2Bis_specialty_care%2C%2Blanguages%2C%2Blocations%2C%2Bmetadata%2C%2Bname%2C%2Bnetwork_affiliations%2C%2Bnetworks%2C%2Bnpi%2C%2Bodhp_open_scheduling%2C%2Bodhp_scheduling_flag%2C%2Bother_video_url%2C%2Bpersonal_interests%2C%2Bphilosophy_of_care_video_url%2C%2Bpractice_groups%2C%2Bprofessional_associations%2C%2Bprofessional_statement%2C%2Bprovider_is_employed%2C%2Bprovider_organization%2C%2Bprovider_title%2C%2Breviews%2C%2Bscope_of_practice%2C%2Bsjh_schedule_provider_num%2C%2Bsjh_scorpion_id%2C%2Bspecialties%2C%2Btraining%2C%2Bxp_publications%2C%2Bappointment_request%2C%2Bappointment_request_url%2C%2Bvirtual_care&filter=networks.network%3AWAProvidence.org%7CMTProvidence.org%7CAKProvidence.org%7CORProvidence.org%7CCAProvidence.org%7COne%20Site%20Providers%7CKadlec%7Cpsjhmedgroups.org&page="
            + str(x)
            + "&per_page=100&shuffle_seed=43f4054621b7499cb96ea87b9859b0a9&sort=relevance%2Cnetworks%2Cdistance&wm_mode=production&wm_type=wmproviders&wm_sort=distance&wm_img_width=300&wm_online_booking_available=false&location=99501&distance=10000&unified=&exact_then_unified=True&typeahead_categories=-ALL%2C%2Bprimary_care%2C%2Bspecialty_synonym%2C%2Bname%2C%2Bclinical_experience%2C%2Bpractice_group&filter=locations.type%3ACLI"
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '{"accepting":' in line:
                items = line.split('{"accepting":')
                for item in items:
                    if '{"address":' in item:
                        locs = item.split('"locations":[')[1].split('{"address":')
                        for loc in locs:
                            if '{"city":"' in loc:
                                city = loc.split('{"city":"')[1].split('"')[0]
                                try:
                                    lurl = loc.split('{"custom":"')[1].split('"')[0]
                                except:
                                    lurl = "<MISSING>"
                                try:
                                    add = loc.split('"plain_street":"')[1].split('"')[0]
                                except:
                                    add = "<MISSING>"
                                try:
                                    state = loc.split('"state":"')[1].split('"')[0]
                                except:
                                    state = "<MISSING>"
                                try:
                                    zc = loc.split('"zip":"')[1].split('"')[0]
                                except:
                                    zc = "<MISSING>"
                                try:
                                    name = loc.split('"name":"')[1].split('"')[0]
                                except:
                                    name = "<MISSING>"
                                try:
                                    phone = loc.split('phone":{"formatted":"')[1].split(
                                        '"'
                                    )[0]
                                except:
                                    phone = "<MISSING>"
                                hours = "<INACCESSIBLE>"
                                try:
                                    lat = loc.split('"lat":')[1].split(",")[0]
                                    lng = loc.split('"lng":')[1].split("}")[0]
                                except:
                                    lat = "<MISSING>"
                                    lng = "<MISSING>"
                                yield SgRecord(
                                    locator_domain=website,
                                    page_url=lurl,
                                    location_name=name,
                                    street_address=add,
                                    city=city,
                                    state=state,
                                    zip_postal=zc,
                                    country_code=country,
                                    phone=phone,
                                    location_type=typ,
                                    store_number=store,
                                    latitude=lat,
                                    longitude=lng,
                                    hours_of_operation=hours,
                                )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
