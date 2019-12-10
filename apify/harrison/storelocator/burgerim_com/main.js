const Apify = require('apify');
const child_process = require("child_process"); 
const util = require('util');
const fs = require('fs-extra');
const csv = util.promisify(require('csv-parse'));  
const glob = require("glob-promise");

const readFileAsync = util.promisify(fs.readFile);
const exec = util.promisify(child_process.exec);

function fail(message) {
	console.log(message);
	process.exit(1);
}

async function listDataFiles() {
	const files = await glob("./apify_storage/datasets/default/*.json");
	return files;
}

async function readDataFiles(files) {
	let pois = [];
	files.forEach(async function(file) {
		const data = await readFileAsync(file, {encoding: "utf8"});
		pois.push(JSON.parse(data));
	});
	return pois;
}

async function pushToCloud() {
	try {
		const files = await listDataFiles();
		const pois = await readDataFiles(files);
		await Apify.pushData(pois);
	} catch(error) {
		console.log(error);
		fail("error parsing output data!");
	}
}

async function runScraper() {
	console.log("in main.js");
	console.log("starting scrape.....");
	const environment = { env: {
		APIFY_LOCAL_STORAGE_DIR: "apify_storage",
		APIFY_CHROME_EXECUTABLE_PATH: "/usr/bin/google-chrome",
		NODE_ENV: "production",
		NODE_PATH: "/usr/local/lib/node_modules/"
	}};
	let err, stdout, stderr;
	try {
		({ err, stdout, stderr } = await exec('node scrape.js', environment));
	} catch(err) {
		fail(`error executing scraper: ${err}`);
	}
	console.log('stdout:', stdout);
	console.log('stderr:', stderr);
}

(async () => {
	await runScraper();
	if (!fs.existsSync('./apify_storage/datasets/default')) {
		fail("scraper did not produce any output data!");
	}
	await pushToCloud();
})();
