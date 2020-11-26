#!/bin/bash

default_target_branch='origin/master'
crawler_subdir_regex='apify(\/[^/]+){3}'

list_diffs() {
	current_branch=$(git rev-parse --abbrev-ref HEAD)
	target_branch="${TARGET_BRANCH:-$default_target_branch}"
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

check_ci_config_current() {
	target_branch="${TARGET_BRANCH:-$default_target_branch}"
	if grep -Eq \
		-e '^\.circleci/config\.yml$' \
		-e '^\.circleci/lib\.sh$' \
		<(git --no-pager diff --name-only "${target_branch}"); then
		echo "FAIL: CI configuration has diverged from ${target_branch}. Please rebase your branch on or merge ${target_branch}."
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
