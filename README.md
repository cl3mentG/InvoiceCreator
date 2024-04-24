# InvoiceCreator

## Description

A simple yet powerful pdf invoice creator.

## Features

- Automatically generates invoice for a customer
- Seller's company identification details, logo...
- Buyer's details
- Shipping and invoicing address
- A table containing the full list of the shopping cart
- A table to recap the order
- Payment details

## Installation

- Install required modules with `pip install -r requirements.txt` (create a venv if you wish)

## Usage

- Run `main.py` and changes the details in `__main__`:
1. Change all details
2. For now, only svg files are supported for logos. No support for .png and .jpg file. These are rasterized file types and should not be used.

## Suggested improvements

- Accept images for logo (.png, .jpg)
- Improve robustness (page breaks...)
- Track and improve overall performance
- Refactor the repository to have a better structure
- Bundle everything to make deployment to serveless (AWS, Azure, GCP) easier : create from JSON
- Provide extended documentation
- Multilanguage support ?