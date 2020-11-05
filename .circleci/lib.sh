#!/bin/bash

crawler_subdir_regex='apify(\/[^/]+){3}'

list_updated_files() {
	current_branch=$(git rev-parse --abbrev-ref HEAD)
	target_branch="${TARGET_BRANCH:-origin/master}"
	git --no-pager diff --name-only "$(git merge-base "$current_branch" "$target_branch")"
}

list_updated_crawlers() {
	list_updated_files |
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
	grep -E '[^.]+\.py$' || true
}

filter_node_files() {
	grep -E '[^.]+\.jsx?$' || true
}

check_update_scope() {
	mapfile -t updated_subdirs < <(list_updated_crawlers)
	updated_files_outside_crawler_subdir=$(list_updated_files | filter_files_outside_crawler_subdir)

	exit_status=0
	if [ -n "$updated_files_outside_crawler_subdir" ]; then
		echo "FAIL: Changes should be confined to a crawler subdirectory, but found changes to the following files:"
		echo "$updated_files_outside_crawler_subdir"
		echo
		exit_status=$((exit_status + 1))
	fi

	if [ "${#updated_subdirs[@]}" -gt 1 ]; then
		echo "FAIL: Changes should be contained in a single crawler subdirectory, but found changes in the following crawler subdirectories:"
		printf '%s\n' "${updated_subdirs[@]}"
		echo
		exit_status=$((exit_status + 2))
	fi

	return $exit_status
}
