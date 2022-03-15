#!/bin/bash

crawler_subdir_regex='apify(\/[^/]+){3}'
required_python_files=('Dockerfile' 'requirements.txt' 'scrape.py')
required_node_files=('Dockerfile' 'scrape.js' 'package.json')
forbidden_files=('chromedriver' 'geckodriver' 'validate.py' 'data.csv' 'state.json')
internal_libraries=('sgscrape' 'sgcrawler' 'sgrequests' 'sgselenium' 'sglogging' 'sgzip' 'sggrid')

function exit_code_of () {
  eval "${1}" 2>1 1>/dev/null
  echo "$?"
}

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
		unpinned_dependencies=$(cat "$requirements_path" | grep -v '\-\-extra-index-url' | awk NF | grep -v '==' || true)
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

function grep_and_get_exit_code() {
  export what="${1}"
  export how="${2}"
  exit_code_of 'echo "${what}" | grep -F "${how}"'
}

check_how_records_are_written_to_file() {
  exit_status=0
  updated_crawler="$(get_updated_crawler)"
  if ! is_node_scraper "$updated_crawler"; then
    script_path="${updated_crawler}/scrape.py"
    script_src="$(cat "$script_path")"
    using_csv_writer="$(grep_and_get_exit_code "$script_src" "csv.writer")"
    using_pandas_csv_writer="$(grep_and_get_exit_code "$script_src" ".to_csv")"
    using_sgwriter="$(grep_and_get_exit_code "$script_src" "SgWriter")"
    using_with_sgwriter="$(grep_and_get_exit_code "$script_src" "with SgWriter")"
    using_deduper="$(grep_and_get_exit_code "$script_src" "SgRecordDeduper")"
    using_ssp="$(grep_and_get_exit_code "$script_src" "SimpleScraperPipeline")"
    using_sgcrawler="$(grep_and_get_exit_code "$script_src" "SgCrawler")"

    if [ "$using_csv_writer" -eq 0 ] || [ "$using_pandas_csv_writer" -eq 0 ]; then
      echo "FAIL: using raw csv writer to write to 'data.csv'. Instead, use SgWriter, SimpleScraperPipeline or SgCrawler"
      exit_status=1
    elif [ "$using_sgwriter" -eq 0 ]; then
      if [ "$using_with_sgwriter" -ne 0 ]; then
        echo "FAIL: when using SgWriter, use the resource-safe version 'with SgWriter(...) as writer'"
        exit_status=1
      elif [ "$using_deduper" -ne 0 ]; then
        echo "FAIL: when using SgWriter, you should also use SgRecordDeduper to deduplicate records."
        exit_status=1
      fi
    elif [ "$using_ssp" -ne 0 ] && [ "$using_sgcrawler" -ne 0 ]; then
      echo "FAIL: The script should use either SgWriter, SimpleScraperPipeline or SgCrawler to write to file"
      exit_status=1
    fi
  fi
  return $exit_status
}

function check_dockerfile_base_image_is_latest() {
  exit_status=0
  updated_crawler="$(get_updated_crawler)"
  if ! is_node_scraper "$updated_crawler" ; then
    docker_path="${updated_crawler}/Dockerfile"
    docker_src="$(cat "$docker_path")"
    using_latest_image="$(grep_and_get_exit_code "$docker_src" 'FROM safegraph/apify-python3:latest')"
    if [ "$using_latest_image" -ne 0 ]; then
      echo "FAIL: Dockerfile should use latest base image: FROM safegraph/apify-python3:latest"
      exit_status=1
    fi
    return $exit_status
  fi
}
