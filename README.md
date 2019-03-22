# Python Fail2Ban Location Mapper
I was interested looking through the log files of fail2ban seeing all the failed attempts, but wanted a way to visualize where all these failed attempts were coming from, thus I wrote this little script.

![Example Image](https://imgur.com/CEFy5Pa.png)

# Installation
*Python 3.6+ Required*

## (Option 1) Using Conda
`conda install --file requirements.txt`

`conda install basemap-data-hires`

## (Option 2) Using pip
    
`pip install requirements.txt`

Then since Basemap isn't included in pip, install Basemap from Matplotlib following the instructions [here]("https://matplotlib.org/basemap/users/installing.html").


# Usage
Read fail2ban log from default location (/var/log/fail2ban.log):

`python main.py -a <IPStack API KEY>`

Specify custom log file

`python main.py -f /path/to/log/file.log -a <IPStack API KEY>`

Output location data in a csv

`python main.py -o data_file_name.csv -a <IPStack API KEY>`

For more infomration

`python main.py --help`

To Generate an IPStack API Key visit [ipstack.com]("https://ipstack.com/")

# TODO's
* Make the request get calls asynchronous