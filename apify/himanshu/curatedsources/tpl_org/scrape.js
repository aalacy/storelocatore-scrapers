const Apify = require('apify');
const esriUtils = require('@esri/arcgis-to-geojson-utils');
const epsg = require('epsg');
const reproject = require('reproject');
const wicket = require('wicket');
const {default: PQueue} = require('p-queue');
const simplify = require('@turf/simplify');
const centroid = require('@turf/centroid').default;
const got = require('got');

function esriJsonEpsg3857ToGeojsonEpsg4326(esriJson) {
	const geoJson = esriUtils.arcgisToGeoJSON(esriJson);
	return reproject.reproject(geoJson, epsg['EPSG:3857'], epsg['EPSG:4326']);
}

function geoJsonToCentroid(geoJson) {
	return centroid(geoJson).geometry.coordinates;
}

function geoJsonToWkt(geoJson) {
	const wkt = new wicket.Wkt();
	if (JSON.stringify(geoJson).length > 250000) {
		geoJson = simplify(geoJson, { tolerance: 0.00001, highQualify: true });
	}
	const parsed = wkt.fromObject(geoJson);
	return parsed.write();
}

function parseCityState(data) {
	try {
		let cityState = data["feature"]["attributes"]["Park_UrbanArea"];
		let parts = cityState.split(',')
		let parsedState = parts[parts.length - 1].trim().split('-')[0].trim();
		let parsedCity = parts.slice(0,-1).join(',').trim().split('-')[0].trim();
		return {
			city: sanitize(parsedCity, '<MISSING>'),
			state: sanitize(parsedState, '<MISSING>')
		};
	} catch(ex) {
		return {
			city: '<MISSING>',
			state: '<MISISNG>'
		};
	}
}

function sanitize(str, defaultValue) {
	if (!str) return defaultValue;
	let stripped = str.replace(/(\r\n|\n|\r)/gm,"").trim();
	return stripped ? stripped : defaultValue;
}

function parseResult(data, itemIndex) {
	const parkId = data["feature"]["attributes"]["ParkID"]?data["feature"]["attributes"]["ParkID"]:"<MISSING>"
	const esriJson = data['feature']['geometry'];
	const geoJson = esriJsonEpsg3857ToGeojsonEpsg4326(esriJson);
	const centroid = geoJsonToCentroid(geoJson);
	let polygonWkt = geoJsonToWkt(geoJson);
	const parsedCityState = parseCityState(data);
	let locationName = sanitize(data["feature"]["attributes"]["Park_Name"], '<MISSING>');
	let streetAddress = sanitize(data["feature"]["attributes"]["Park_Address_1"], locationName);
	const item = {
		locator_domain: "https://www.tpl.org",
		location_name: locationName,
		street_address: streetAddress, 
		city:parsedCityState.city,
		state:parsedCityState.state,
		zip:"<MISSING>",
		country_code:"US",
		store_number:parkId,
		phone:"<MISSING>",
		location_type: "<MISSING>",
		latitude: centroid[1] ? centroid[1] : '<MISSING>',
		longitude: centroid[0] ? centroid[0] : '<MISSING>',
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
	if (itemIndex >= 128000 && itemIndex <= 129000) {
		return undefined;
	}
	try {
		const url = `${BASE_URL}/${itemIndex}?f=pjson`;
		const response = await got(url, { timeout: { lookup: 10000, connect: 10000, secureConnect: 10000, response: 20000 }, retry: { retries: 3, errorCodes: ['ETIMEDOUT', 'ECONNRESET', 'EADDRINUSE', 'ECONNREFUSED', 'EPIPE', 'ENOTFOUND', 'ENETUNREACH', 'EAI_AGAIN', 'ECONNABORTED']}, json: true});
		const data = response.body;
		if (!data || data.hasOwnProperty("error")) {
			return undefined;
		} else {
			return parseResult(data, itemIndex);
		}
	} catch(exce) {
		console.log(`itemIndex: ${itemIndex}`);
		console.log(exce);
		errors++;
		console.log(`error count: ${errors}`);
	}
}

async function scrapeBatch(startIndex, size) {
	const queue = new PQueue({concurrency: 70});
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
