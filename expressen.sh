#!/bin/bash

#expressen menu
#$1: <#days from today>
#$2: <language> (en for English, default is Swedish)
lunch() {
	#number of days from today
	local ndays=0

	local lang='sv_SE.utf-8'
	if equals $2 en; then
		lang='en_US.utf8'
	fi

	#check if input null
	if ! isempty $1; then
		#check if input digit or negative
		if ! isdigit $1 || isnegative $1; then
			echo -e "\nInvalid input\n"
			return 0
		fi
		ndays=$1
	fi

	local today=$(date +'%Y-%m-%d')
	local todate=$(date -d "$today+$ndays days" +'%Y-%m-%d')

	#api url
	local url=$(expressen_url)

	#get data
	expressen_data $2
	if isempty $rawdata; then
		echo -e "\nNo data\n"
		return 0
	fi

	#store data in array
	toarray

	#map food to formatd dates in order to sort by date
	declare -A local newdata
	format

	#sort data because of shitty json
	IFS=';'
	read -r -a sorted -d '' <<<"$(
		for key in "${!newdata[@]}"; do
			printf "%s\n" "$key ${newdata[$key]}"
		done | sort -k1
	)"
	unset IFS

	#init colors etc.
	style

	#print data
	print $2
}

#expressen data, default language: SV
expressen_data() {
	#get EN or SV menu
	local arg=0
	if equals $1 en; then
		arg=1
	fi

	rawdata=$(curl -s $url | jq -r 'sort_by(.startDate) |
	 (.[] | .startDate, .displayNames['$arg'].dishDisplayName)')
}

#expressen api
expressen_url() {
	local hostname='http://carbonateapiprod.azurewebsites.net/'
	local api='api/v1/mealprovidingunits/3d519481-1667-4cad-d2a3-08d558129279/dishoccurrences'
	echo ''$hostname''$api'?startDate='$today'&endDate='$todate''
}

#date is stored as '4/23/2019 12:00:00 AM' in shitty json,
#+ which is a not valid format
toarray() {
	#IFS (internal field separator) variable is used to determine what characters
	#+ bash defines as words boundaries when processing character strings.
	IFS=$'\n'

	#store data in array
	read -r -a data -d '' <<<"$rawdata"

	#reset back to default value
	unset IFS
}

format() {
	local -r dateformat='+%Y-%m-%d'
	local length=${#data[@]}
	for ((i = 0; i < $length; i += 2)); do

		local date=${data[i]}
		local food=${data[$((i + 1))]}
		local formated=$(date --date "$date" $dateformat)
		local prev=${newdata[$formated]}

		#store dates as keys mapping to food, meat and/or veg
		if isempty $prev; then
			newdata+=([$formated]=";$food;")
		else
			newdata[$formated]="$prev$food;"
		fi
	done
}

print() {
	local length=${#sorted[@]}
	for ((i = 0; i < $length; i += 1)); do

		local wildcard=${sorted[i]}

		if isdate $wildcard; then
			local day=$(LC_TIME=$lang date --date "$wildcard" +'%a')
			echo -e "\n${bold}${green}${day}${default}"
		elif ! isempty $wildcard; then

			is_it_meatballs $1

			if ! isempty $index; then
				printfood
			else
				echo $wildcard
			fi

		fi
	done
	echo ""
}

#return index if string contains 'köttbullar' or meatballs
#does not work properly for matched words after special characters...
is_it_meatballs() {
	ingredient='köttbullar'
	if equals $1 en; then
		ingredient='meatballs'
	fi
	index="$(echo $wildcard | grep -bio $ingredient | grep -oE '[0-9]+')"
}

printfood() {
	local foodend="$(echo $ingredient | awk '{print length}')"
	local end=$(($index + $foodend))

	local head="${wildcard:0:$index}"
	local body="${blink}${bold}${orange}${wildcard:$index:$foodend}"
	local tail="${default}${wildcard:$end}"

	echo -e "${head}${body}${tail}"
}

style() {
	default='\e[0m'
	bold='\e[1m'
	blink='\e[39m\e[5m'
	green='\e[32m'
	orange='\e[38;5;208m'
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

isdate() {
	[[ "$1" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] && date -d "$1" >/dev/null
}

lunch $1 $2
