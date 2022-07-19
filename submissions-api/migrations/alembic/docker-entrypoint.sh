#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2022 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

# vim: set noexpandtab ts=4 sw=4 nolist:
set -Eeo pipefail

if [ "$#" -eq 0 ]; then
	if [ -z "${DB_URI}" ]; then
		echo "You need to set the DB_URI environment variable."
		exit 1
	fi
	# migrate to head if no arguments
	alembic -c /migrations/alembic.ini upgrade head

elif [ "$1" = 'autogenerate' ]; then
	if [ -z "${DB_URI}" ]; then
		echo "You need to set the DB_URI environment variable."
		exit 1
	fi
	# autogenerate a revision
	alembic -c /migrations/alembic.ini revision --autogenerate

else
	# Run command as given by user
	exec "$@"
fi
