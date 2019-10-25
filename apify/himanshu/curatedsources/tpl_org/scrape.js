const Apify = require('apify');
const esriUtils = require('@esri/arcgis-to-geojson-utils');
const epsg = require('epsg');
const reproject = require('reproject');
const wicket = require('wicket');
const polygonCenter = require('geojson-polygon-center')
const axios = require('axios');
const {default: PQueue} = require('p-queue');
const axiosRetry = require('axios-retry');

axiosRetry(axios, { retries: 3, shouldResetTimeout: true, retryCondition: (error) => {
  return axiosRetry.isNetworkOrIdempotentRequestError(error) || error.code === 'ECONNABORTED';
}});

function esriJsonEpsg3857ToGeojsonEpsg4326(esriJson) {
	const geoJson = esriUtils.arcgisToGeoJSON(esriJson);
	return reproject.reproject(geoJson, epsg['EPSG:3857'], epsg['EPSG:4326']);
}

function geoJsonToCentroid(geoJson) {
	return polygonCenter(geoJson).coordinates;
}

function geoJsonToWkt(geoJson) {
	const wkt = new wicket.Wkt();
	const parsed = wkt.fromObject(geoJson);
	return parsed.write();
}

function parseResult(data, itemIndex) {
	const parkId = data["feature"]["attributes"]["ParkID"]?data["feature"]["attributes"]["ParkID"]:"<MISSING>"
	const esriJson = data['feature']['geometry'];
	const geoJson = esriJsonEpsg3857ToGeojsonEpsg4326(esriJson);
	const centroid = geoJsonToCentroid(geoJson);
	let polygonWkt = geoJsonToWkt(geoJson);
	if (polygonWkt.length > 100000) {
		console.log('found a large wkt!');
		polygonWkt = '<MISSING>'
	}
	const item = {
		locator_domain: "https://www.tpl.org",
		location_name:data["feature"]["attributes"]["Park_Name"]?data["feature"]["attributes"]["Park_Name"]:"<MISSING>",
		street_address: data["feature"]["attributes"]["Park_Address_1"]?data["feature"]["attributes"]["Park_Address_1"]:"<MISSING>",
		city:data["feature"]["attributes"]["Park_UrbanArea"]?data["feature"]["attributes"]["Park_UrbanArea"]: "<MISSING>",
		state:data["feature"]["attributes"]["Park_UrbanArea"]?data["feature"]["attributes"]["Park_UrbanArea"]:"<MISSING>",
		zip:"<MISSING>",
		country_code:"US",
		store_number:parkId,
		phone:"<MISSING>",
		location_type: "<MISSING>",
		latitude: centroid[1],
		longitude: centroid[0],
		hours_of_operation:"<MISSING>",
		page_url:`https://server3.tplgis.org/arcgis3/rest/services/ParkServe/ParkServe_Parks/MapServer/0/${itemIndex}?f=pjson`,
		wkt:polygonWkt
	}
	return item;
}

const BASE_URL = 'https://server3.tplgis.org/arcgis3/rest/services/ParkServe/ParkServe_Parks/MapServer/0'

let errors = 0;
async function scrapeItem(itemIndex) {
	if (itemIndex % 1000 == 0) console.log(itemIndex);
	try {
		const url = `${BASE_URL}/${itemIndex}?f=pjson`;
		const res = await axios.get(url, { timeout: 20000 });
		const data = res.data;
		if (!data || data.hasOwnProperty("error")) {
			return undefined;
		} else {
			return parseResult(data, itemIndex);
		}
	} catch(exce) {
		console.log(`itemIndex: ${itemIndex}`);
		if (typeof res !== 'undefined') console.log(res.body);
		console.log(exce);
		errors++;
		console.log(`error count: ${errors}`);
	}
}

async function scrapeBatch(startIndex, size) {
	const queue = new PQueue({concurrency: 100});
	let promises = [];
	for (let i = 0; i < size; i++) {
		const itemIndex = startIndex + i;
		promises.push(() => { return scrapeItem(itemIndex) });
	}
	const results = await queue.addAll(promises);
	return results.filter((result) => !!result);
}

const BATCH_SIZE = 10000;

Apify.main(async () => {
	let stop = false;
	let startIndex = 1;
	while (!stop) {
		const currentBatch = await scrapeBatch(startIndex, BATCH_SIZE);
		if (currentBatch.length < BATCH_SIZE / 2) {
			stop = true;
		}
		startIndex += BATCH_SIZE;
		console.log(`${currentBatch.length} items retrieved`);
		await Apify.pushData(currentBatch);
	}
});
