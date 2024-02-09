# BSL Automatic PSD Calculator

## Description

This repository contains a version of the IRIS DMC Noise Toolkit that has been modified for use by the Berkeley Seismology Lab. Files have been created/altered to provide new methods of waveform/metadata analysis and smoother integration with visualization on Grafana.

### Latest Release
This latest release under Python 3 includes:
- A new script `ntk_extractPsdPeriod.py`
  - Given the necessary parameters, computes the Power Spectral Density (PSD) from requested stations and extracts all instances of the specified period/frequency into one file.

## Usage

The modified PDF/PSD package contains all existing features in the original package. If the desired script to run is not found below, please refer to https://github.com/iris-edu/noise-toolkit for more information.

### Parameter Input

Previously, the IRIS Noise Toolkit required a manual input of parameters through a terminal. All the available parameters have been migrated to the `noise-toolkit/param/` directory for greater efficiency and ability to pipeline auto-generated values over repeated execution of the script.

### ntk_autoPSD

`ntk_autoPSD` combines `ntk_computePSD`, `ntk_extractPsdDay`, and `ntk_extractPeriodPsd` all into one chained function, allowing for an automated extraction of all density plot values from the specified station that compiles into a collection of data, one file for each 24-hour period. The parameters to configure `ntk_autoPSD` can be found in `param/autoPSD.json`. Specifications for each parameter is listed below:

```
data_center	[default: FDSN] client to use to make data/metadata requests (FDSN or FILES) 
net		[required] network code
sta		[required] station code
loc		[required] location ID
chan		[default: BH?] channel ID(s); separate multiple channel codes by comma (no space)
xtype		[period or frequency, default: period] X-axis type (period or frequency for outputs and plots)
start		[required] start date-time (UTC) of the interval for which PSDs to be computed (format YYYY-MM-DDTHH:MM:SS)
end		[required] end date-time (UTC) of the interval for which PSDs to be computed (format YYYY-MM-DDTHH:MM:SS)
window_length [default: 3600] the period of time each batch of PSD extraction spans over, in seconds
directory [required] the output directory path for extracted PSD files to be written to
```

### ntk_extractPeriodPsd
Given a time period, station, and desired period/frequency in `param/extractPsdPeriod.json`, this script extracts all the PSD values present at the specified period or frequency value. Each PSD value in the resulting file (located in the `data/psdPr`) will be preceded by every instance of date and hour that falls between the previously defined time range.  
  
For example, running `ntk_extractPeriodPsd` with `start=2023-01-29T01:00:00` and `end=2023-01-29T03:00:00` will output the following file in `data/psdPr`:
```
2023-01-29  01:00:00    -57
2023-01-29  01:30:00    -57
2023-01-29  02:00:00    -57
2023-01-29  02:30:00    -56
```

### ntk_extractPsdDay
A modified version of `ntk_extractPsdHour` from the IRIS Noise Toolkit, this function now divides the specified period of time (over which requests to the stations will be made) into 24-hour periods for a single-day summary of the seismic activity recorded. Files created from `ntk_extractPsdDay` always end at the 00:00 hour mark, which means that running the script with a start or end time deviating from 00:00 results in an extra file capturing a period of time less than 24 hours.


## More information

For comments or questions, please contact sylvesterseo@berkeley.edu
