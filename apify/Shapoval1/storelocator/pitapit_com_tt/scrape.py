import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_locations():

    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    }

    url = "https://www.google.com/maps/vt?pb=!1m4!1m3!1i10!2i336!3i481!1m4!1m3!1i10!2i337!3i481!1m4!1m3!1i10!2i336!3i482!1m4!1m3!1i10!2i337!3i482!1m4!1m3!1i10!2i338!3i481!1m4!1m3!1i10!2i338!3i482!2m3!1e0!2sm!3i578303513!2m74!1e2!2sspotlight!5i1!8m70!11e11!12m46!1spita+pit!2m2!1s104961730291851993832!2s!3m1!3s0x0%3A0xb458e84991fb649f!3m1!3s0x0%3A0xb3a22dcdf95c5b07!3m1!3s0x0%3A0xea29ea1ad27b941f!3m1!3s0x0%3A0x2c7ff52bcf79599d!3m1!3s0x0%3A0xac667ad5303009d3!3m1!3s0x0%3A0xbec118d861ff6848!3m1!3s0x0%3A0xe18c82ec002a7497!3m1!3s0x0%3A0x8e09a6f8dcc05a2!3m1!3s0x0%3A0x8cd3590f2e6fcf5e!3m1!3s0x0%3A0x11c7783c6a44fa07!3m1!3s0x0%3A0x9610511de57b6ba1!3m1!3s0x0%3A0x97821a40e9018cdf!3m1!3s0x0%3A0x65d8fcae4289460e!3m1!3s0x0%3A0x905f6c7f67718ce6!3m1!3s0x0%3A0xd6b0106401156ab2!3m1!3s0x0%3A0x21e8bf7963481835!3m1!3s0x0%3A0x20139bc6a2314350!3m1!3s0x0%3A0x59a22e2f8668f797!3m1!3s0x0%3A0x2e4a27d1e80303c6!3m1!3s0x0%3A0x68407e508c9b0828!10b0!20e3!13m14!2sa!14b1!18m7!5b0!6b0!9b0!12b1!16b0!20b1!21b1!22m3!6e2!7e3!8e2!19u12!19u14!19u29!19u37!19u30!19u61!19u70!3m12!2sen!3sTT!5e289!12m4!1e68!2m2!1sset!2sRoadmap!12m3!1e37!2m1!1ssmartmaps!4e3!12m1!5b1&client=google-maps-embed&token=53563"
    r = session.get(url, headers=headers)
    data_json = r.json()

    list_of_ids = []
    location_names_list = []
    for i in data_json:
        try:
            features = i["features"]
            for j in features:
                list_of_ids.append(j["id"])
                data_json_2 = j["c"]
                data_json_2c = json.loads(data_json_2)
                locname = data_json_2c["1"]["title"]
                location_names_list.append(locname)
        except Exception:
            pass
    location_names_list = [locname.replace(" ", "+") for locname in location_names_list]
    locname_and_id = dict(zip(list_of_ids, location_names_list))

    url_gmaps_as_getentitydetails = "https://www.google.com/maps/api/js/ApplicationService.GetEntityDetails?pb=!1m6!1m5!2s"
    url_dimension = "!3m2!1d!2d!4s"
    url_locations = []

    for id_, locname in locname_and_id.items():
        url_store_data = f"{url_gmaps_as_getentitydetails}{locname}{url_dimension}{id_}"
        url_locations.append(url_store_data)

    return url_locations


def fetch_data(sgw: SgWriter):

    urls = get_locations()
    locator_domain = "https://pitapit.com.tt/"
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    }

    for url in urls:
        r = session.get(url, headers=headers)

        d = eval(r.text.split(")]}'\n")[-1].replace("null", '""'))[1]
        page_url = "https://pitapit.com.tt/"
        ad = "".join(d[0][1])
        location_name = ad.split(",")[0].strip()
        latitude, longitude = d[0][2]
        street_address = "".join(d[2][0])
        city = ad.split(",")[-2].replace("St. Augustine Campus", "").strip()
        street_address = street_address.replace(f"{city}", "").strip()
        country_code = "TT"
        phone = d[7] or "<MISSING>"

        _tmp = []
        try:
            for i in d[-1][0]:
                day = i[0]
                time = i[3][0][0]
                _tmp.append(f"{day}: {time}")
        except:
            pass
        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
