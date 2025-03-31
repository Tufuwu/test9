#!/bin/bash

# handy script for autogenerating release notes from GitHub merged PRs
# not perfect, but easy to update if we want to change it up in the future

last_tag=$(git tag --list | egrep '^[[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+$' | sort -V | tail -n 1)

github-issue-title () {
    local reponame="globus/globus-cli"
	local num="$1"
	api_out="$(curl --silent \
        "https://api.github.com/repos/$reponame/issues/$num")"
	echo "$api_out" | grep '"title"' | cut -d':' -f2- | sed -e 's/^ "//' -e 's/",$//'
}

git log "${last_tag}..master" --oneline | grep 'Merge pull' | egrep -o '#[[:digit:]]+' | tr -d '#' | \
    while read line; do
        echo "* $(github-issue-title "$line")"
        echo "(https://github.com/globus/globus-cli/pull/${line}[${line}])"
    done
