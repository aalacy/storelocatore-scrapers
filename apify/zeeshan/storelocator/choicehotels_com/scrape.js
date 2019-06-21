const Apify = require('apify');
const child_process = require("child_process"); 
const util = require('util');
const fs = require('fs-extra');
const csv = util.promisify(require('csv-parse'));  
const mapKeys = require('lodash.mapkeys');

(async () => {
	console.log("starting scrape.....");
	const exec = util.promisify(child_process.exec);
	await exec('python choicehotels.py');

	let data = await fs.readFile('choicehotels.csv');
	let parsed = await csv(data);
	console.log(`${parsed.count} rows parsed`);
	let header = parsed[0];
	let translation = {...header}
	let rows = parsed.slice(1);
	let pois = rows.map((row) => mapKeys({...row}, (value, key) => { return translation[key]; } ));
	await Apify.pushData(pois);
})();
