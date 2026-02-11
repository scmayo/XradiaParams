# XradiaParams
Python app for grabbing Tomography scan metadata from Xradia TXRM file

Zeiss Xradia Tomography systems such as the Versa 5**, 6** (and perhaps 7**) store data from tomography scans in a proprietary file format with extension ".txrm"

This format is based on the OLE file format which can be read using the olefiles python library. This app uses this library to extract a useful subset of metadata for a scan.
