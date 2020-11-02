const Apify = require('apify');
const child_process = require("child_process"); 
const util = require('util');
const fs = require('fs-extra');
const csv = util.promisify(require('csv-parse'));  
const mapKeys = require('lodash.mapkeys');

function fail(message) {
	console.log(message);
	process.exit(1);
}

(async () => {
	console.log("starting scrape.....");
	const exec = util.promisify(child_process.exec);
	let err, stdout, stderr;
	try {
		({ err, stdout, stderr } = await exec('python3 scrape.py'));
	} catch(err) {
		fail("error executing python scraper!");
	}
	console.log('stdout:', stdout);
	console.log('stderr:', stderr);

	if (!fs.existsSync('data.csv')) {
		fail("python scraper did not produce a data.csv file!");
	}

	let data = await fs.readFile('data.csv');
	let pois;
	try {
		let parsed = await csv(data);
		if (parsed.length <= 1) {
			fail("data.csv has no rows");
		}
		let header = parsed[0];
		let translation = {...header}
		let rows = parsed.slice(1);
		pois = rows.map((row) => mapKeys({...row}, (value, key) => { return translation[key]; } ));
	} catch {
		fail("error parsing data.csv file!");
	}
	await Apify.pushData(pois);
})();
