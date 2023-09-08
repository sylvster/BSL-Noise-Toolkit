# BSL Automatic PSD Calculator

## Description

This repository contains a version of the IRIS DMC Noise Toolkit that has been modified for use by the Berkeley Seismology Lab. Files have been created/altered to provide new methods of waveform/metadata analysis and smoother integration with visualization on Grafana.

### Latest Release
This latest release under Python 3 includes:
- A new script `ntk_extractPsdPeriod.py`
  - Given the necessary parameters, computes the Power Spectral Density (PSD) from requested stations and extracts all instances of the specified period/frequency into one file.

## Usage

The modified PDF/PSD package contains all existing features in the original package. If the desired script to run is not found below, please refer to https://github.com/iris-edu/noise-toolkit for more information.

### ntk_extractPeriodPsd
Given a time period, station, and desired period/frequency in `param/extractPsdPeriod.json`, this script extracts all the PSD values present at the specified period or frequency value. Each PSD value in the resulting file (located in the `data/psdPr`) will be preceded by every instance of date and hour that falls between the previously defined time range.  
  
For example, running `ntk_extractPeriodPsd` with `start=2023-01-29T01:00:00` and `end=2023-01-29T03:00:00` will output the following file in `data/psdPr`:
```
2023-01-29  01:00:00    -57
2023-01-29  01:30:00    -57
2023-01-29  02:00:00    -57
2023-01-29  02:30:00    -56
```

## More information

For comments or questions, please contact sylvesterseo@berkeley.edu
