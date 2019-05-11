#!/usr/bin/env bash
install_express () {
	export FILE="express"
	curl "https://raw.githubusercontent.com/lasanjin/expressen-lunch-cli/master/expressen.py" > ~/$FILE
	chmod +x ~/$FILE
	sudo mv ~/$FILE /usr/local/bin
}
install_express