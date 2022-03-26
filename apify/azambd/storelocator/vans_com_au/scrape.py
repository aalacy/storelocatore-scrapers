import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "https://www.vans.com.au"
MISSING = SgRecord.MISSING

headers = {
    "authority": "www.vans.com.au",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-newrelic-id": "VQcDVFdTDxABXVJbBgUPVVI=",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.vans.com.au/stores/",
    "accept-language": "en-US,en;q=0.9,bn;q=0.8",
    "cookie": "_ga=GA1.3.1670612144.1647578136; form_key=Vm7U5KkTUShNaj1Q; _gcl_au=1.1.998422751.1647578137; wisepops=%7B%22csd%22%3A1%2C%22popups%22%3A%7B%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A5%2C%22cid%22%3A%2249455%22%2C%22v%22%3A4%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D; wisepops_wsb-1.1.0-VPqt6sepze-session=%7B%22id%22%3A%22ab227e01-91e5-498f-a944-138fc23ae8a3%22%2C%22start%22%3A1647578136822%7D; lantern=ce7ce642-7df6-4060-8319-3f221a9f6dd6; BVBRANDID=2a86835d-83d1-406e-8929-0441f54d6060; tfc-l=%7B%22k%22%3A%7B%22v%22%3A%22ug4bps0erpkm9s13njvugkmr02%22%2C%22e%22%3A1710477338%7D%7D; SLISYNC=1; SLIBeacon=s9mm6o5b9o1647578139554boo62lfo; __zlcmid=193kmeWqroLMQ6v; sqvisitor=id=bb4156db-7ab7-42ce-8103-764330c5d1cb; gs_v_GSN-296339-M=; _hjSessionUser_1669875=eyJpZCI6IjgwMjRiMmQxLTIzMGItNTlkZS1iNzBmLTU5YTcyY2U3NjMwYyIsImNyZWF0ZWQiOjE2NDc1NzgxMzY4NDAsImV4aXN0aW5nIjp0cnVlfQ==; form_key=Vm7U5KkTUShNaj1Q; PHPSESSID=aba5upnm0g7nc4rgda242fu29o; mage-cache-storage=%7B%7D; mage-cache-storage-section-invalidation=%7B%7D; _gid=GA1.3.547242543.1648143388; mage-cache-sessid=true; recently_viewed_product=%7B%7D; recently_viewed_product_previous=%7B%7D; recently_compared_product=%7B%7D; recently_compared_product_previous=%7B%7D; product_data_storage=%7B%7D; mage-messages=; mage-banners-cache-storage=%7B%7D; _hjSession_1669875=eyJpZCI6ImI4M2Q4NjYwLWFlNWUtNDA0ZS04NGNhLTU4MjY0NWY0NzkyMCIsImNyZWF0ZWQiOjE2NDgxNDMzOTAxMzEsImluU2FtcGxlIjp0cnVlfQ==; _clck=14kayfe|1|f01|0; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=1; _hjIncludedInSessionSample=1; BVBRANDSID=31921436-813b-4c9e-8efc-99a3b6e31186; sqsess=id=82096e89-907e-472a-8800-864bf48382b0; sqshowmaintenance.1514247712=false; wisepops_activity_session=%7B%22id%22%3A%2268338054-9e05-437d-9a38-7de061642b4d%22%2C%22start%22%3A1648147095629%7D; vans-australia-7-1-foursixty-cache-storage=%7B%7D; cto_bundle=y43HQF91Qk1UM2N5RDlKRCUyRjdVQXEyemFnM2g0amRpcjU3N2VDa0tSVFElMkJ5VEthZGFJNFBVV3pza0FnOFJVeURpclUlMkJ3JTJGdDFIWVlaWWQzSVM3UXNrJTJCcnJYMWlNJTJCRUQxTjc1bk1wblo4Q2Z3UjFXWEV1SEFYMyUyRk53cll2WGIxRkFlcUlSMWpyVUNRJTJCMnB3b1Bkc0dhVWpOJTJGNzVlcXM3d2J4eUJSTVM2V0ZFRThUSlUlM0Q; RT=nu=https%3A%2F%2Fwww.vans.com.au%2Fstores%2F%23storelocator_region_form&cl=1648147534949&r=https%3A%2F%2Fwww.vans.com.au%2Fstores%2F&ul=1648147677901; _gat=1; wisepops_visits=%5B%222022-03-24T18%3A47%3A58.342Z%22%2C%222022-03-24T18%3A38%3A15.591Z%22%2C%222022-03-24T18%3A33%3A56.363Z%22%2C%222022-03-24T18%3A24%3A40.864Z%22%2C%222022-03-24T18%3A20%3A36.676Z%22%2C%222022-03-24T18%3A20%3A19.488Z%22%2C%222022-03-24T17%3A38%3A40.973Z%22%2C%222022-03-24T17%3A36%3A28.477Z%22%2C%222022-03-18T04%3A35%3A36.223Z%22%5D; wisepops_session=%7B%22arrivalOnSite%22%3A%222022-03-24T18%3A47%3A58.342Z%22%2C%22mtime%22%3A1648147678434%2C%22pageviews%22%3A1%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22utm%22%3A%7B%7D%2C%22testIp%22%3Anull%7D; _uetsid=f01bcd90ab9811ec9ca6ed9ad9f7bcf5; _uetvid=db51c9c0a67411ec9d76a95bfa33aba4; gs_u_GSN-296339-M=80b51d433914805d9f13ef8e3681f4d0:6403:9169:1648147681581; 16692.vst=%7B%22s%22%3A%22cebd08df-4ecc-4430-a187-68896672e8fa%22%2C%22t%22%3A%22returning%22%2C%22lu%22%3A1648147681708%2C%22lv%22%3A1648143392798%2C%22lp%22%3A0%7D; _clsk=1afv1hi|1648147685782|14|1|h.clarity.ms/collect; datadome=hIpQ6PmwhbXgWq-vEG1LUaP.KZFme8fzDl.RTCmMFXaUtlLnHXRGYr_X_LYQLdr00~KB6cSzIlmYuH5cqKoqzultQCIBhi1_RnOeuX5H0Pq5SfmSqrE_7roH_hHH550; datadome=PvWw55hMeIcKnrUQv.ROiRt1v47.nYu9WjA81R6Y8DzAVjG7j-5jZ8JL6jjb~Bg5RsloVmkmuoPuaa.DDa3WiN73R4pbVYzQcTuwwA8TiLG73EobsY-eM6DSSZxqtJN; PHPSESSID=aba5upnm0g7nc4rgda242fu29o; form_key=Vm7U5KkTUShNaj1Q",
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def get_response(url):
    return session.get(url, headers=headers)


def fetch_stores():
    region_ids = ["512", "513", "514", "515", "516", "519"]
    stores = []
    count = 0
    for region_id in region_ids:
        count = count + 1
        url = f"{website}/rest/V1/storelocator/search?searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bfield%5D=lat&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bfield%5D=lng&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bfield%5D=country_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bvalue%5D=AU&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bfield%5D=region_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bvalue%5D={region_id}&sarchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bfield%5D=region&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bfield%5D=distance&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bvalue%5D=50&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bfield%5D=onlyLocation&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bvalue%5D=0&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bcondition_type%5D=eq&searchCriteria%5Bpage_size%5D=5&_=1648147678180"
        response = get_response(url)
        log.info(f"Response Status: {response}")
        if response.status_code != 200:
            log.error(f"{region_id}. not found {response.status_code}")
            continue
        items = json.loads(response.text)["items"]
        log.info(f"{count}. from {region_id} stores = {len(items)}")
        stores.extend(items)
    return stores


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


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    store_number = MISSING
    location_type = MISSING
    country_code = "AU"
    page_url = f"{website}/stors"

    for store in stores:
        location_name = get_JSON_object_variable(store, "name")
        street_address = get_JSON_object_variable(store, "street")
        city = get_JSON_object_variable(store, "city")
        zip_postal = get_JSON_object_variable(store, "postal_code")
        state = get_JSON_object_variable(store, "state_name")
        phone = get_JSON_object_variable(store, "phone")
        latitude = get_JSON_object_variable(store, "lat")
        longitude = get_JSON_object_variable(store, "lng")
        hoo = get_JSON_object_variable(store, "working_hours", "{}")
        hoo = json.loads(hoo)
        hours_of_operation = []
        for key in hoo.keys():
            h = hoo[key]
            hours_of_operation.append(f"{h['day'].strip()}: {h['value'].strip()}")
        hours_of_operation = "; ".join(hours_of_operation)
        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

        yield SgRecord(
            locator_domain="vans.com.au",
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=location_type,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
    return []


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
