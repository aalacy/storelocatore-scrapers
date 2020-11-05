#!/bin/sh

list_updated_files() {
	target_branch="${TARGET_BRANCH:-remotes/origin/master}"
	git diff --name-only "$(git merge-base --fork-point "$target_branch")"
}

get_updated_python_files() {
	list_updated_files | grep -E '[^.]+\.py$' || true | tr '\n' ' '
}

get_updated_node_files() {
	list_updated_files | grep -E '[^.]+\.jsx?$' || true | tr '\n' ' '
}

check_update_scope() {
	crawler_regex='apify(\/[^/]+){3}'

	updated_crawlers=$(list_updated_files |
		xargs -I{} dirname {} |
		sort |
		uniq |
		grep -E "$crawler_regex" || true)

	updated_non_crawler_files=$(list_updated_files | grep -E -v "$crawler_regex" || true)

	status_code=0
	if [ -n "$updated_non_crawler_files" ]; then
		echo "FAIL: Ordinary PRs must not change files outside of a crawler subdirectory, but found changes to the following files:"
		echo "$updated_non_crawler_files"
		echo
		status_code=$((status_code + 1))
	fi
	if [ "$(echo "$updated_crawlers" | wc -l)" -gt 1 ]; then
		echo "FAIL: Ordinary PRs must change files in exactly one crawler subdirectory, but found changes in the following crawler subdirectories:"
		echo "$updated_crawlers"
		echo
		status_code=$((status_code + 2))
	fi
	return $status_code
}
