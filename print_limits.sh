#!/bin/sh

limits() {
    cat $1/limits.json | python -c "import sys, json; print json.load(sys.stdin)[u'1000.0'][u'exp0']"
}

for d in ${@}; do
    if [[ -d $d/limits/ ]]; then
	limits $d/limits/
    fi
done
