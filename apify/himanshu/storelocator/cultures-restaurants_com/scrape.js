const Apify = require('apify');
const child_process = require("child_process"); 
const util = require('util');
const fs = require('fs-extra');
const csv = util.promisify(require('csv-parse'));  
const mapKeys = require('lodash.mapkeys');

(async () => {
	console.log("starting scrape.....");
	const exec = util.promisify(child_process.exec);
	let err, stdout, stderr;
	try {
		({ err, stdout, stderr } = await exec('python3 scrape.py'));
	} catch(err) {
		console.log("error executing python scraper!");
		process.exit(1);
	}
	console.log('stdout:', stdout);
	console.log('stderr:', stderr);

	if (!fs.existsSync('data.csv')) {
		console.log("python scraper did not produce a data.csv file");
		process.exit(1);
	}

	let data = await fs.readFile('data.csv');
	let parsed = await csv(data);
	if (parsed.length <= 1) {
		console.log("data.csv has no rows");
		process.exit(1);
	}
	let header = parsed[0];
	let translation = {...header}
	let rows = parsed.slice(1);
	let pois = rows.map((row) => mapKeys({...row}, (value, key) => { return translation[key]; } ));
	await Apify.pushData(pois);
})();
