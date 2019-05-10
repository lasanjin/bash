#!/usr/bin/env bash
install_express () {
	export FILE="express"
	curl "https://raw.githubusercontent.com/lasanjin/expressen-lunch-cli/master/expressen.py" > ~/Downloads/$FILE
	chmod +x ~/Downloads/$FILE
	mv ~/Downloads/$FILE /usr/local/bin
}
install_express