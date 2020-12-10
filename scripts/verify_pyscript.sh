#!/bin/bash

#echo $@

script=$1
s_dir=$(dirname "$script")
s_name=$(basename "$script")

$(
	rm -rf $s_dir/__pycache__
	cd $s_dir
	python3 -m py_compile $s_name
	cmp_result=$?
	rm -rf $s_dir/__pycache__

	if [ $cmp_result -ne 0 ]; then
		echo ">> Compiler error: $script"
	fi

	pylint -E $s_name
	cmp_result=$?
	if [ $cmp_result -ne 0 ]; then
		echo ">> Linter error: $script"
	fi
)
