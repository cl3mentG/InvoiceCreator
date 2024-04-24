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
- Multilanguage support ?

## Documentation for Invoice

`Invoice()` initializes an instance of the InvoiceGenerator class. Its attributes have to be set manually.
After setting the attributes, `generate_pdf()` method can be called.

Public methods:
- `generate_pdf (name: str)` : `name` is the desired name for the output file. Name must not include file extension ".pdf".
    The function will generate the pdf invoice from with information pvovided.

Attributes: all attributes are public.
- `company_name`: The name of the company.
- `company_logo: str`: The logo of the company. This is string containing the .svg file content.
- `company_VAT_number`: The VAT number of the company.
- `company_registration_number`: The registration number of the company.
- `company_email`: The email address of the company.
- `company_address`: The address of the company.
- `company_zip_city`: The ZIP code and city of the company.
- `company_phone`: The phone number of the company.
- `customer_number`: *optional* The customer number. 
- `customer_name`: The name of the customer.
- `invoice_number`: The invoice number.
- `invoice_date`: The date of the invoice.
- `due_date`: The due date of the invoice.
- `invoicing_address`: *optional* The invoicing address.
- `invoicing_zip_city`: *optional* The ZIP code and city for invoicing.
- `invoicing_phone`: *optional* The phone number for invoicing.
- `invoicing_email`: *optional* The email address for invoicing.
- `shipping_address`: *optional* The shipping address.
- `shipping_zip_city`: *optional* The ZIP code and city for shipping.
- `shipping_phone`: *optional* The phone number for shipping.
- `shipping_email`: *optional* The email address for shipping.
- `items: List[Tuple[str, str, number, number]]`: The list of items in the invoice. Items have to be passed with the following format: a list or tuple of `title: str, description: str, quantity : number, price: number`. Description is optional, leave `""` if no description.
- `VAT_rate: number`: The VAT rate for the invoice.
- `discount: number`: The discount for the invoice.
- `payment_terms : List[str]`: The payment terms for the invoice. Each element of the input list is displayed on a new line