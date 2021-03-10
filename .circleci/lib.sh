#!/bin/bash

crawler_subdir_regex='apify(\/[^/]+){3}'
required_python_files=('Dockerfile' 'requirements.txt' 'scrape.py')
required_node_files=('Dockerfile' 'scrape.js' 'package.json')
forbidden_files=('chromedriver' 'geckodriver' 'validate.py' 'data.csv')
internal_libraries=('sgscrape' 'sgcrawler' 'sgrequests' 'sgselenium' 'sglogging' 'sgzip' 'sggrid')

list_diffs() {
	current_branch=$(git rev-parse --abbrev-ref HEAD)
	target_branch="${TARGET_BRANCH:-origin/master}"
	git --no-pager diff ${1:+"$1"} --name-only "$(git merge-base "$current_branch" "$target_branch")"
}

list_updated_files() {
	list_diffs --diff-filter=d
}

list_updated_crawlers() {
	list_diffs "" |
		xargs -I{} dirname {} |
		sort |
		uniq |
		grep -E "$crawler_subdir_regex" || true
}

get_updated_crawler() {
	mapfile -t updated_subdirs < <(list_updated_crawlers)
	echo "${updated_subdirs[0]}"
}

filter_files_outside_crawler_subdir() {
	grep -E -v "$crawler_subdir_regex" || true
}

filter_python_files() {
	grep -E '\.py$' || true
}

filter_node_files() {
	grep -E '\.jsx?$' || true
}

ensure_no_linter_config() {
	if [ -e "$1" ]; then
		echo "FAIL: Crawler-specific linting configuration is not allowed. Please remove '$1'"
		return 1
	fi
}

check_diffs() {
	mapfile -t updated_subdirs < <(list_updated_crawlers)
	diffs_outside_crawler_subdir=$(list_diffs "" | filter_files_outside_crawler_subdir)

	exit_status=0
	if [ -n "$diffs_outside_crawler_subdir" ]; then
		echo "FAIL: Diffs should be limited to a crawler subdirectory, but found changes to the following files:"
		echo "$diffs_outside_crawler_subdir"
		echo
		exit_status=$((exit_status + 1))
	fi

	if [ "${#updated_subdirs[@]}" -gt 1 ]; then
		echo "FAIL: Diffs should be limited to a single crawler subdirectory, but found changes in the following crawler subdirectories:"
		printf '%s\n' "${updated_subdirs[@]}"
		echo
		exit_status=$((exit_status + 2))
	fi

	updated_crawler="${updated_subdirs[0]}"

	ensure_no_linter_config "${updated_crawler}/.eslintrc.json" || exit_status=$((exit_status + 4))
	ensure_no_linter_config "${updated_crawler}/.flake8" || exit_status=$((exit_status + 8))

	return $exit_status
}

is_node_scraper() {
	num_js_files=$(find "$1" | filter_node_files | wc -l)
	if [ "$num_js_files" -gt 0 ]; then
		true
	else
		false
	fi
}

check_required_file() {
	if [ ! -f "${1}/${2}" ]; then
		echo "FAIL: Your scraper is missing a required file: ${2}."
		return 1
	fi
}

check_forbidden_file() {
	if [ -f "${1}/${2}" ]; then
		echo "FAIL: Your scraper contains a forbidden file: ${2}."
		return 1
	fi
}

check_required_files() {
	exit_status=0
	updated_crawler="$(get_updated_crawler)"
	if is_node_scraper "$updated_crawler"; then
		for required_file in "${required_node_files[@]}"; do
			check_required_file "${updated_crawler}" "${required_file}" || exit_status=1
		done
	else
		for required_file in "${required_python_files[@]}"; do
			check_required_file "${updated_crawler}" "${required_file}" || exit_status=1
		done
	fi
	return $exit_status
}

check_forbidden_files() {
	exit_status=0
	updated_crawler="$(get_updated_crawler)"
	for forbidden_file in "${forbidden_files[@]}"; do
		check_forbidden_file "${updated_crawler}" "${forbidden_file}" || exit_status=1
	done
	return $exit_status
}

check_dependencies() {
	exit_status=0
	updated_crawler="$(get_updated_crawler)"
	if ! is_node_scraper "$updated_crawler"; then
		requirements_path="${updated_crawler}/requirements.txt"
		unpinned_dependencies=$(cat "$requirements_path" | awk NF | grep -v '==' || true)
		if [ ! -z "$unpinned_dependencies" ]; then
			formatted_unpinned_dependencies="${unpinned_dependencies//$'\n'/', '}"
			echo "FAIL: found unpinned dependencies in requirements.txt: $formatted_unpinned_dependencies"
			exit_status=1
		fi
	fi
	return $exit_status
}

# https://stackoverflow.com/a/17841619
join_by() {
	local d=$1
	shift
	local f=$1
	shift
	printf %s "$f" "${@/#/$d}"
}

check_internal_library_versions() {
	exit_status=0
	updated_crawler="$(get_updated_crawler)"
	if ! is_node_scraper "$updated_crawler"; then
		requirements_path="${updated_crawler}/requirements.txt"
		internal_library_regex="$(join_by "|" "${internal_libraries[@]}")"
		outdated_internal_libraries=$(piprot --outdated "$requirements_path" | grep -E "$internal_library_regex" || true)
		if [ -n "$outdated_internal_libraries" ]; then
			formatted_outdated_internal_libraries="${outdated_internal_libraries//$'\n'/', '}"
			echo "FAIL: found outdated SafeGraph libraries in requirements.txt: $formatted_outdated_internal_libraries"
			exit_status=1
		fi
	fi
	return $exit_status

}
