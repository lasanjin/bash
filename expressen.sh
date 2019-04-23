#!/bin/bash

#expressen menu
#$1: <#days from today>
#$2: <language> (s for swedish, default is english)
lunch() {
	#number of days from today
	local ndays=0

	#check if input null
	if ! isempty $1; then
		ndays=$1

		#check if input digit or negative
		if ! isdigit $1 || isnegative $1; then
			echo -e "\nInvalid input\n"
			return 0
		fi
	fi

	local today=$(date +'%Y-%m-%d')
	local todate=$(date -d "$today+$ndays days" +'%Y-%m-%d')

	#api url
	expressen_url
	local URL=''$url'?startDate='$today'&endDate='$todate''

	#get data
	expressen_data "$URL" "$2"
	local data=$expressen_data

	if isempty "$data"; then
		echo -e "\nNo data\n"
		return 0
	fi

	#store data in array
	toarray "$data"
	arr=$arr

	#init colors etc.
	style

	local SV='sv_SE.utf-8'
	declare local tempdate
	local length=${#arr[@]}

	#data is stored: [date0, meat0, date0, veg0, date1, meat1, date1, veg1, ...]
	#+ because of shitty json
	for ((i = 0; i < $length; i += 2)); do

		local date=${arr[i]}
		local food=${arr[$((i + 1))]}

		if isvalid "$date" "$food"; then
			if ! equals "$date" "$tempdate"; then
				if equals $2 s; then
					#swedish
					dag=$(LC_TIME=$SV date --date "$date" +'%A')
					echo -e "\n${bold}${green}${dag}${default}:"
				else
					#english
					day=$(date --date "$date" +'%A')
					echo -e "\n${bold}${green}${day}${default}:"
				fi

				tempdate=$date
			fi

			is_it_meatballs "$food" "$2"
			index=$index
			end="$(echo $ingredient | awk '{print length}')"

			if ! isempty $index; then
				echo -e "${blink}${bold}${red}${food:$index:$end}${default}${food:$end}"
			else
				echo -e "$food"
			fi
		fi
	done

	echo -e ""
}

#expressen data, default language: EN
expressen_data() {
	#get EN or SV menu
	local lang=1
	if equals $2 s; then
		lang=0
	fi

	#sort because of shitty json
	expressen_data=$(curl -s $1 | jq -r 'sort_by(.startDate) |
	 (.[] | .startDate, .displayNames['$lang'].dishDisplayName)')
}

#expressen api
expressen_url() {
	local api='v1/mealprovidingunits/3d519481-1667-4cad-d2a3-08d558129279/dishoccurrences'
	url='http://carbonateapiprod.azurewebsites.net/api/'$api''
}

#return index if string contains 'MEATBALLS' or 'KöTTBULLAR'
is_it_meatballs() {
	ingredient='MEATBALLS'
	if equals $2 s; then
		ingredient='KöTTBULLAR'
	fi

	local capital="$(echo $1 | tr a-z A-Z)"
	index="$(echo $capital | grep -b -o $ingredient | awk 'BEGIN {FS=":"}{print $1}')"
}

#date is stored as '4/23/2019 12:00:00 AM' in shitty json,
#+ which is a not valid format
toarray() {
	#IFS (internal field separator) variable is used to determine what characters
	#+ bash defines as words boundaries when processing character strings.
	IFS=$'\n'

	#store data in array
	read -r -a arr -d '' <<<"$data"

	#reset back to default value
	unset IFS
}

style() {
	default='\e[0m'
	bold='\e[1m'
	blink='\e[39m\e[5m'
	green='\e[32m'
	red='\e[31m'
}

equals() {
	[ "$1" == "$2" ]
}

isempty() {
	[ -z "$1" ]
}

isdigit() {
	[[ "$1" =~ ^[0-9]*$ ]]
}

isnegative() {
	[ $1 -lt 0 ]
}

isvalid() {
	[ "$1" != "null" ] && [ "$2" != "null" ]
}

lunch $1 $2
