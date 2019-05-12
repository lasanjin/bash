#!/usr/bin/env bash
install_clunch () {
	export FILE="clunch"
	curl "https://raw.githubusercontent.com/lasanjin/chalmers-lunch-cli/master/clunch.py" > ~/$FILE
	chmod +x ~/$FILE
	sudo mv ~/$FILE /usr/local/bin
}
install_clunch