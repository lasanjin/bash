## Description
Gets, sorts & outputs Chalmers expressen lunch menu in terminal & highlights "Meatballs" or "Köttbullar" from Chalmers expressen lunch [api](http://carbonateapiprod.azurewebsites.net/api/v1/mealprovidingunits/3d519481-1667-4cad-d2a3-08d558129279/dishoccurrences?startDate=2019-04-22&endDate=2019-05-03). 

<img src="expressen-GIF.gif" width="640">

## Get jq
Alt 1
1. Install jq
```
$ sudo apt-get install jq
```

Alt 2
1. Download jq
```
$ wget https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64
```
2. Make script executable
```
$ sudo chmod +x ./jq-linux64.sh 
```
3. Replace `jq` with `./jq-linux64` in `expressen_data()` function


## How to run
1. Make script executable
```
$ sudo chmod +x ./expressen.sh 
```

2. Run script
```
$ ./expressen.sh $1 $2
```
- `$1`
  -  *optional* 
  -  #days from today
     -  input `0-9`, default is today's menu
- `$2` 
  - *optional*
  - language
    - input `en` for English menu, default is Swedish