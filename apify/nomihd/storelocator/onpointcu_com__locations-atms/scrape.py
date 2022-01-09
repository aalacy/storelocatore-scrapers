# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "onpointcu.com/locations-atms"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.onpointcu.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "text/html, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.onpointcu.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.onpointcu.com/locations-atms/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

id_list = []


def fetch_records_for(zipcode):
    log.info(f"pulling records for coordinates: {zipcode}")
    search_url = "https://www.onpointcu.com/wp-content/plugins/pixelspoke-atm-map/public/ajax-apiToggle.php"
    data = [
        ("$text", zipcode),
        ("latLng[lat]", ""),
        ("latLng[lng]", ""),
        ("zip", zipcode),
        ("atms", "no"),
        ("sharedbranches", "no"),
        ("lsFilters[]", "FCS"),
        ("lsFilters[]", "ATMSF"),
        ("lsFilters[]", "ATMDP"),
        ("fromDrag", "false"),
        ("showNearby", "false"),
        ("haveGeo", "false"),
        ("firstMapLoaded", "true"),
        ("isInitialPageLoad", "false"),
        ("isZipSearch", "false"),
        ("locationTalley", ""),
        ("mapPinOverrides[0][override_key]", "LocationName"),
        ("mapPinOverrides[0][override_value]", "OnPoint University of Oregon"),
        ("mapPinOverrides[0][override_pin][ID]", "16103"),
        ("mapPinOverrides[0][override_pin][id]", "16103"),
        ("mapPinOverrides[0][override_pin][title]", "Deposit Taking ATMs icon"),
        (
            "mapPinOverrides[0][override_pin][filename]",
            "map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][filesize]", "447"),
        (
            "mapPinOverrides[0][override_pin][url]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        (
            "mapPinOverrides[0][override_pin][link]",
            "https://www.onpointcu.com/map_pin_onpoint_green-01/",
        ),
        ("mapPinOverrides[0][override_pin][alt]", "Deposit Taking ATMs icon"),
        ("mapPinOverrides[0][override_pin][author]", "33"),
        ("mapPinOverrides[0][override_pin][description]", ""),
        ("mapPinOverrides[0][override_pin][caption]", ""),
        ("mapPinOverrides[0][override_pin][name]", "map_pin_onpoint_green-01"),
        ("mapPinOverrides[0][override_pin][status]", "inherit"),
        ("mapPinOverrides[0][override_pin][uploaded_to]", "0"),
        ("mapPinOverrides[0][override_pin][date]", "2019-03-21 20:27:58"),
        ("mapPinOverrides[0][override_pin][modified]", "2019-03-21 20:28:45"),
        ("mapPinOverrides[0][override_pin][menu_order]", "0"),
        ("mapPinOverrides[0][override_pin][mime_type]", "image/svg+xml"),
        ("mapPinOverrides[0][override_pin][type]", "image"),
        ("mapPinOverrides[0][override_pin][subtype]", "svg+xml"),
        (
            "mapPinOverrides[0][override_pin][icon]",
            "https://www.onpointcu.com/wp-includes/images/media/default.png",
        ),
        ("mapPinOverrides[0][override_pin][width]", ""),
        ("mapPinOverrides[0][override_pin][height]", ""),
        (
            "mapPinOverrides[0][override_pin][sizes][thumbnail]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][sizes][thumbnail-width]", ""),
        ("mapPinOverrides[0][override_pin][sizes][thumbnail-height]", ""),
        (
            "mapPinOverrides[0][override_pin][sizes][medium]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][sizes][medium-width]", ""),
        ("mapPinOverrides[0][override_pin][sizes][medium-height]", ""),
        (
            "mapPinOverrides[0][override_pin][sizes][medium_large]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][sizes][medium_large-width]", ""),
        ("mapPinOverrides[0][override_pin][sizes][medium_large-height]", ""),
        (
            "mapPinOverrides[0][override_pin][sizes][large]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][sizes][large-width]", ""),
        ("mapPinOverrides[0][override_pin][sizes][large-height]", ""),
        (
            "mapPinOverrides[0][override_pin][sizes][1536x1536]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][sizes][1536x1536-width]", ""),
        ("mapPinOverrides[0][override_pin][sizes][1536x1536-height]", ""),
        (
            "mapPinOverrides[0][override_pin][sizes][2048x2048]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][sizes][2048x2048-width]", ""),
        ("mapPinOverrides[0][override_pin][sizes][2048x2048-height]", ""),
        (
            "mapPinOverrides[0][override_pin][sizes][tiny]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][sizes][tiny-width]", ""),
        ("mapPinOverrides[0][override_pin][sizes][tiny-height]", ""),
        (
            "mapPinOverrides[0][override_pin][sizes][small]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][sizes][small-width]", ""),
        ("mapPinOverrides[0][override_pin][sizes][small-height]", ""),
        (
            "mapPinOverrides[0][override_pin][sizes][hero-large]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][sizes][hero-large-width]", ""),
        ("mapPinOverrides[0][override_pin][sizes][hero-large-height]", ""),
        (
            "mapPinOverrides[0][override_pin][sizes][hero-medium]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][sizes][hero-medium-width]", ""),
        ("mapPinOverrides[0][override_pin][sizes][hero-medium-height]", ""),
        (
            "mapPinOverrides[0][override_pin][sizes][community-giving-focus]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][sizes][community-giving-focus-width]", ""),
        ("mapPinOverrides[0][override_pin][sizes][community-giving-focus-height]", ""),
        (
            "mapPinOverrides[0][override_pin][sizes][join-explainer]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[0][override_pin][sizes][join-explainer-width]", ""),
        ("mapPinOverrides[0][override_pin][sizes][join-explainer-height]", ""),
        ("mapPinOverrides[1][override_key]", "AcceptDeposit"),
        ("mapPinOverrides[1][override_value]", "Deposit Taking"),
        ("mapPinOverrides[1][override_pin][ID]", "16103"),
        ("mapPinOverrides[1][override_pin][id]", "16103"),
        ("mapPinOverrides[1][override_pin][title]", "Deposit Taking ATMs icon"),
        (
            "mapPinOverrides[1][override_pin][filename]",
            "map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][filesize]", "447"),
        (
            "mapPinOverrides[1][override_pin][url]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        (
            "mapPinOverrides[1][override_pin][link]",
            "https://www.onpointcu.com/map_pin_onpoint_green-01/",
        ),
        ("mapPinOverrides[1][override_pin][alt]", "Deposit Taking ATMs icon"),
        ("mapPinOverrides[1][override_pin][author]", "33"),
        ("mapPinOverrides[1][override_pin][description]", ""),
        ("mapPinOverrides[1][override_pin][caption]", ""),
        ("mapPinOverrides[1][override_pin][name]", "map_pin_onpoint_green-01"),
        ("mapPinOverrides[1][override_pin][status]", "inherit"),
        ("mapPinOverrides[1][override_pin][uploaded_to]", "0"),
        ("mapPinOverrides[1][override_pin][date]", "2019-03-21 20:27:58"),
        ("mapPinOverrides[1][override_pin][modified]", "2019-03-21 20:28:45"),
        ("mapPinOverrides[1][override_pin][menu_order]", "0"),
        ("mapPinOverrides[1][override_pin][mime_type]", "image/svg+xml"),
        ("mapPinOverrides[1][override_pin][type]", "image"),
        ("mapPinOverrides[1][override_pin][subtype]", "svg+xml"),
        (
            "mapPinOverrides[1][override_pin][icon]",
            "https://www.onpointcu.com/wp-includes/images/media/default.png",
        ),
        ("mapPinOverrides[1][override_pin][width]", ""),
        ("mapPinOverrides[1][override_pin][height]", ""),
        (
            "mapPinOverrides[1][override_pin][sizes][thumbnail]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][sizes][thumbnail-width]", ""),
        ("mapPinOverrides[1][override_pin][sizes][thumbnail-height]", ""),
        (
            "mapPinOverrides[1][override_pin][sizes][medium]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][sizes][medium-width]", ""),
        ("mapPinOverrides[1][override_pin][sizes][medium-height]", ""),
        (
            "mapPinOverrides[1][override_pin][sizes][medium_large]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][sizes][medium_large-width]", ""),
        ("mapPinOverrides[1][override_pin][sizes][medium_large-height]", ""),
        (
            "mapPinOverrides[1][override_pin][sizes][large]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][sizes][large-width]", ""),
        ("mapPinOverrides[1][override_pin][sizes][large-height]", ""),
        (
            "mapPinOverrides[1][override_pin][sizes][1536x1536]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][sizes][1536x1536-width]", ""),
        ("mapPinOverrides[1][override_pin][sizes][1536x1536-height]", ""),
        (
            "mapPinOverrides[1][override_pin][sizes][2048x2048]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][sizes][2048x2048-width]", ""),
        ("mapPinOverrides[1][override_pin][sizes][2048x2048-height]", ""),
        (
            "mapPinOverrides[1][override_pin][sizes][tiny]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][sizes][tiny-width]", ""),
        ("mapPinOverrides[1][override_pin][sizes][tiny-height]", ""),
        (
            "mapPinOverrides[1][override_pin][sizes][small]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][sizes][small-width]", ""),
        ("mapPinOverrides[1][override_pin][sizes][small-height]", ""),
        (
            "mapPinOverrides[1][override_pin][sizes][hero-large]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][sizes][hero-large-width]", ""),
        ("mapPinOverrides[1][override_pin][sizes][hero-large-height]", ""),
        (
            "mapPinOverrides[1][override_pin][sizes][hero-medium]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][sizes][hero-medium-width]", ""),
        ("mapPinOverrides[1][override_pin][sizes][hero-medium-height]", ""),
        (
            "mapPinOverrides[1][override_pin][sizes][community-giving-focus]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][sizes][community-giving-focus-width]", ""),
        ("mapPinOverrides[1][override_pin][sizes][community-giving-focus-height]", ""),
        (
            "mapPinOverrides[1][override_pin][sizes][join-explainer]",
            "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg",
        ),
        ("mapPinOverrides[1][override_pin][sizes][join-explainer-width]", ""),
        ("mapPinOverrides[1][override_pin][sizes][join-explainer-height]", ""),
        ("mapPinOverrides[2][override_key]", "LocationName"),
        ("mapPinOverrides[2][override_value]", "OnPoint OHSU Physician's Pavilion"),
        ("mapPinOverrides[2][override_pin][ID]", "1502"),
        ("mapPinOverrides[2][override_pin][id]", "1502"),
        ("mapPinOverrides[2][override_pin][title]", "map_pin_onpoint_teal"),
        ("mapPinOverrides[2][override_pin][filename]", "map_pin_onpoint_teal.svg"),
        ("mapPinOverrides[2][override_pin][filesize]", "291"),
        (
            "mapPinOverrides[2][override_pin][url]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        (
            "mapPinOverrides[2][override_pin][link]",
            "https://www.onpointcu.com/map_pin_onpoint_teal/",
        ),
        ("mapPinOverrides[2][override_pin][alt]", "OnPoint ATM Map Pin"),
        ("mapPinOverrides[2][override_pin][author]", "33"),
        ("mapPinOverrides[2][override_pin][description]", ""),
        ("mapPinOverrides[2][override_pin][caption]", ""),
        ("mapPinOverrides[2][override_pin][name]", "map_pin_onpoint_teal"),
        ("mapPinOverrides[2][override_pin][status]", "inherit"),
        ("mapPinOverrides[2][override_pin][uploaded_to]", "0"),
        ("mapPinOverrides[2][override_pin][date]", "2018-10-26 22:42:14"),
        ("mapPinOverrides[2][override_pin][modified]", "2018-10-26 22:42:23"),
        ("mapPinOverrides[2][override_pin][menu_order]", "0"),
        ("mapPinOverrides[2][override_pin][mime_type]", "image/svg+xml"),
        ("mapPinOverrides[2][override_pin][type]", "image"),
        ("mapPinOverrides[2][override_pin][subtype]", "svg+xml"),
        (
            "mapPinOverrides[2][override_pin][icon]",
            "https://www.onpointcu.com/wp-includes/images/media/default.png",
        ),
        ("mapPinOverrides[2][override_pin][width]", ""),
        ("mapPinOverrides[2][override_pin][height]", ""),
        (
            "mapPinOverrides[2][override_pin][sizes][thumbnail]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        ("mapPinOverrides[2][override_pin][sizes][thumbnail-width]", ""),
        ("mapPinOverrides[2][override_pin][sizes][thumbnail-height]", ""),
        (
            "mapPinOverrides[2][override_pin][sizes][medium]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        ("mapPinOverrides[2][override_pin][sizes][medium-width]", ""),
        ("mapPinOverrides[2][override_pin][sizes][medium-height]", ""),
        (
            "mapPinOverrides[2][override_pin][sizes][medium_large]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        ("mapPinOverrides[2][override_pin][sizes][medium_large-width]", ""),
        ("mapPinOverrides[2][override_pin][sizes][medium_large-height]", ""),
        (
            "mapPinOverrides[2][override_pin][sizes][large]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        ("mapPinOverrides[2][override_pin][sizes][large-width]", ""),
        ("mapPinOverrides[2][override_pin][sizes][large-height]", ""),
        (
            "mapPinOverrides[2][override_pin][sizes][1536x1536]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        ("mapPinOverrides[2][override_pin][sizes][1536x1536-width]", ""),
        ("mapPinOverrides[2][override_pin][sizes][1536x1536-height]", ""),
        (
            "mapPinOverrides[2][override_pin][sizes][2048x2048]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        ("mapPinOverrides[2][override_pin][sizes][2048x2048-width]", ""),
        ("mapPinOverrides[2][override_pin][sizes][2048x2048-height]", ""),
        (
            "mapPinOverrides[2][override_pin][sizes][tiny]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        ("mapPinOverrides[2][override_pin][sizes][tiny-width]", ""),
        ("mapPinOverrides[2][override_pin][sizes][tiny-height]", ""),
        (
            "mapPinOverrides[2][override_pin][sizes][small]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        ("mapPinOverrides[2][override_pin][sizes][small-width]", ""),
        ("mapPinOverrides[2][override_pin][sizes][small-height]", ""),
        (
            "mapPinOverrides[2][override_pin][sizes][hero-large]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        ("mapPinOverrides[2][override_pin][sizes][hero-large-width]", ""),
        ("mapPinOverrides[2][override_pin][sizes][hero-large-height]", ""),
        (
            "mapPinOverrides[2][override_pin][sizes][hero-medium]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        ("mapPinOverrides[2][override_pin][sizes][hero-medium-width]", ""),
        ("mapPinOverrides[2][override_pin][sizes][hero-medium-height]", ""),
        (
            "mapPinOverrides[2][override_pin][sizes][community-giving-focus]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        ("mapPinOverrides[2][override_pin][sizes][community-giving-focus-width]", ""),
        ("mapPinOverrides[2][override_pin][sizes][community-giving-focus-height]", ""),
        (
            "mapPinOverrides[2][override_pin][sizes][join-explainer]",
            "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg",
        ),
        ("mapPinOverrides[2][override_pin][sizes][join-explainer-width]", ""),
        ("mapPinOverrides[2][override_pin][sizes][join-explainer-height]", ""),
        ("mapPinOverrides[3][override_key]", "LocationName"),
        ("mapPinOverrides[3][override_value]", "*OnPoint*"),
        ("mapPinOverrides[3][override_pin][ID]", "1501"),
        ("mapPinOverrides[3][override_pin][id]", "1501"),
        ("mapPinOverrides[3][override_pin][title]", "map_pin_onpoint_orange"),
        ("mapPinOverrides[3][override_pin][filename]", "map_pin_onpoint_orange.svg"),
        ("mapPinOverrides[3][override_pin][filesize]", "291"),
        (
            "mapPinOverrides[3][override_pin][url]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        (
            "mapPinOverrides[3][override_pin][link]",
            "https://www.onpointcu.com/map_pin_onpoint_orange/",
        ),
        ("mapPinOverrides[3][override_pin][alt]", "OnPoint Branch Map Pin"),
        ("mapPinOverrides[3][override_pin][author]", "33"),
        ("mapPinOverrides[3][override_pin][description]", ""),
        ("mapPinOverrides[3][override_pin][caption]", ""),
        ("mapPinOverrides[3][override_pin][name]", "map_pin_onpoint_orange"),
        ("mapPinOverrides[3][override_pin][status]", "inherit"),
        ("mapPinOverrides[3][override_pin][uploaded_to]", "0"),
        ("mapPinOverrides[3][override_pin][date]", "2018-10-26 22:39:33"),
        ("mapPinOverrides[3][override_pin][modified]", "2018-10-26 22:39:43"),
        ("mapPinOverrides[3][override_pin][menu_order]", "0"),
        ("mapPinOverrides[3][override_pin][mime_type]", "image/svg+xml"),
        ("mapPinOverrides[3][override_pin][type]", "image"),
        ("mapPinOverrides[3][override_pin][subtype]", "svg+xml"),
        (
            "mapPinOverrides[3][override_pin][icon]",
            "https://www.onpointcu.com/wp-includes/images/media/default.png",
        ),
        ("mapPinOverrides[3][override_pin][width]", ""),
        ("mapPinOverrides[3][override_pin][height]", ""),
        (
            "mapPinOverrides[3][override_pin][sizes][thumbnail]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        ("mapPinOverrides[3][override_pin][sizes][thumbnail-width]", ""),
        ("mapPinOverrides[3][override_pin][sizes][thumbnail-height]", ""),
        (
            "mapPinOverrides[3][override_pin][sizes][medium]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        ("mapPinOverrides[3][override_pin][sizes][medium-width]", ""),
        ("mapPinOverrides[3][override_pin][sizes][medium-height]", ""),
        (
            "mapPinOverrides[3][override_pin][sizes][medium_large]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        ("mapPinOverrides[3][override_pin][sizes][medium_large-width]", ""),
        ("mapPinOverrides[3][override_pin][sizes][medium_large-height]", ""),
        (
            "mapPinOverrides[3][override_pin][sizes][large]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        ("mapPinOverrides[3][override_pin][sizes][large-width]", ""),
        ("mapPinOverrides[3][override_pin][sizes][large-height]", ""),
        (
            "mapPinOverrides[3][override_pin][sizes][1536x1536]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        ("mapPinOverrides[3][override_pin][sizes][1536x1536-width]", ""),
        ("mapPinOverrides[3][override_pin][sizes][1536x1536-height]", ""),
        (
            "mapPinOverrides[3][override_pin][sizes][2048x2048]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        ("mapPinOverrides[3][override_pin][sizes][2048x2048-width]", ""),
        ("mapPinOverrides[3][override_pin][sizes][2048x2048-height]", ""),
        (
            "mapPinOverrides[3][override_pin][sizes][tiny]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        ("mapPinOverrides[3][override_pin][sizes][tiny-width]", ""),
        ("mapPinOverrides[3][override_pin][sizes][tiny-height]", ""),
        (
            "mapPinOverrides[3][override_pin][sizes][small]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        ("mapPinOverrides[3][override_pin][sizes][small-width]", ""),
        ("mapPinOverrides[3][override_pin][sizes][small-height]", ""),
        (
            "mapPinOverrides[3][override_pin][sizes][hero-large]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        ("mapPinOverrides[3][override_pin][sizes][hero-large-width]", ""),
        ("mapPinOverrides[3][override_pin][sizes][hero-large-height]", ""),
        (
            "mapPinOverrides[3][override_pin][sizes][hero-medium]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        ("mapPinOverrides[3][override_pin][sizes][hero-medium-width]", ""),
        ("mapPinOverrides[3][override_pin][sizes][hero-medium-height]", ""),
        (
            "mapPinOverrides[3][override_pin][sizes][community-giving-focus]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        ("mapPinOverrides[3][override_pin][sizes][community-giving-focus-width]", ""),
        ("mapPinOverrides[3][override_pin][sizes][community-giving-focus-height]", ""),
        (
            "mapPinOverrides[3][override_pin][sizes][join-explainer]",
            "https://www.onpointcu.com/files/map_pin_onpoint_orange.svg",
        ),
        ("mapPinOverrides[3][override_pin][sizes][join-explainer-width]", ""),
        ("mapPinOverrides[3][override_pin][sizes][join-explainer-height]", ""),
        ("mapExtraInfoAtms", "false"),
        ("isCuMarkers[0][key]", "LocationName"),
        ("isCuMarkers[0][value]", "*OnPoint*"),
    ]
    stores = []
    search_res = session.post(search_url, data=data, headers=headers)
    try:
        json_str = search_res.text.split("locationData =")[1].split("}],")[0] + "}]"
        stores = json.loads(json_str)
    except:
        pass

    return stores


def process_record(raw_results_from_one_zipcode):
    # Your scraper here
    store_list = raw_results_from_one_zipcode

    for store in store_list:

        page_url = "<MISSING>"
        if "customAtmInfo" in store:
            page_url = store["customAtmInfo"]
            if page_url:
                page_url = page_url.split('href="')[1].split('"')[0]

        locator_domain = website

        location_name = store["name"]

        street_address = store["address"]["street"]

        city = store["address"]["city"]
        state = store["address"]["state"]
        zip = store["address"]["zip"]

        country_code = "US"

        store_number = store["id"]
        if store_number in id_list:
            continue

        id_list.append(store_number)
        phone = store["phone"]

        location_type = store["type"]
        if location_type == "branch":
            location_type = "branch and ATM"

        if (
            store["customPinUrl"]
            == "https://www.onpointcu.com/files/map_pin_onpoint_green-01-1.svg"
        ):
            location_type = location_type + ", Deposit Taking ATMs"
        elif (
            store["customPinUrl"]
            == "https://www.onpointcu.com/files/map_pin_onpoint_teal.svg"
        ):
            location_type = location_type + ", Surcharge-Free ATMs"

        if store["is_cu_branch"] is True:
            location_type = location_type + ", CU BRANCH"

        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        hours = []
        hour_info = store["hours"]
        for day in days:
            hours.append(
                f'{day}: {"closed" if not hour_info.get(day) else hour_info[day]}'
            )

        hours_of_operation = "; ".join(hours)

        latitude, longitude = store["latitude"], store["longitude"]
        raw_address = "<MISSING>"

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = parallelize(
            search_space=static_zipcode_list(
                radius=5, country_code=SearchableCountries.USA
            ),
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
            max_threads=20,  # tweak to see what's fastest
        )
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
