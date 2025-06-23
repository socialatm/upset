Reads the past 5 years of betting history from betmma.tips and creates a csv file with the data.

Currently takes about 25 minutes to run.

to run it:
```python
py scraper.py
```
## testing

Open _**scraper.py**_ and change _line 11_ to true.
```python
testing = False # Set to True for testing with limited data
```

* only scrapes the first 5 links
* saves data to _**test.csv**_ file
* prints test mode message on the screen
* takes under a minute to test changes instead of the 25 minutes it takes to run the script.
