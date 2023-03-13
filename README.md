# polyspace-report2excel

polyspace-report2excel is a python module which adds the possibility 
to read a polyspace report and export misra or run-time results in 
an excel file for easier analyse.

## Installation

pip insall polyspace-report2excel

## Usage
Export polyspace data in an HTML report or RTF report then run export-all.py, you can use `--help`. 

Script was made for polyspace 2018 but you can run it with polyspace 2014 
by adding `--poly14` argument.

By default it export all tables to excel and generate one file per Polyspace chapter.
Use arguments to filter what you need.

``` 
python export-all.py input.html ouput-folder/
# OR
## WARNING, by converting RTF file you must precise --runtime or --misra
python export-all.py input.rtf ouput-folder/ --runtime
```
## Arguments
- `--misra` will export misra report only.
- `--runtime` will export run-time report only (ignored if `--misra`).
- `-y` will force overwrite if output files already exist.
- `--poly14` will read report from polyspace 2014
- `--csv` will export data in CSV instead of xlsx

## Create you own export script
You can also create you own script if needed. With `HTMLReader` you can 
extract all tables from report to python variables, do some operations 
and finally write to excel with `exportxlsx`. You can use `export-all.py`
as example or see docstrings inside `HTMLReader` or `exportxlsx`.
