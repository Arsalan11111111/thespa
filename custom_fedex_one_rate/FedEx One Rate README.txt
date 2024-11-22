FedEx One Rate Integration with Saturday Delivery and Overnight Upgrade
Overview
The custom_fedex_one_rate module integrates FedEx One Rate into Odoo and provides options for Saturday delivery and overnight upgrades for destinations within 150 miles. This module applies the shipping cost to the cost field on orders, supporting separate customer-facing pricing if needed.

Key Features
FedEx One Rate integration for flat-rate pricing based on eligible packaging and services.
Saturday Delivery for orders placed by Thursday, subject to availability.
Overnight Upgrade option for orders within 150 miles, upgrading to overnight shipping if eligible.
Installation Instructions
1. Prepare the Module Files
Download and Copy Module:

Copy the custom_fedex_one_rate folder (containing __init__.py, __manifest__.py, and the models folder) into the addons directory of your Odoo installation.
Set Permissions (if necessary):

bash
Copy code
sudo chown -R odoo:odoo /path/to/odoo/addons/custom_fedex_one_rate
sudo chmod -R 755 /path/to/odoo/addons/custom_fedex_one_rate
2. Update the Odoo Module List
Activate Developer Mode:

In Odoo, navigate to Settings > General Settings and enable Developer Mode.
Update Apps List:

Go to Apps in Odoo, click on Update Apps List, and confirm to refresh the module list.
3. Install the Module
Search for “FedEx One Rate Integration”:
In Apps, search for the module by name and click Install.
4. Configuration
Set Up FedEx API Credentials:

Go to Inventory > Configuration > Shipping Methods and configure your FedEx API credentials, including:
API Key
Account Number
Meter Number
Authentication Key
Configure Eligible Packaging Types:

Ensure packaging types used for FedEx One Rate (e.g., FedEx Small Box) are set up for your shipping methods.
Technical Documentation
Module Structure
bash
Copy code
custom_fedex_one_rate/
├── __init__.py            # Module initializer
├── __manifest__.py        # Module metadata
└── models/
    ├── __init__.py        # Model initializer
    └── fedex_one_rate.py  # Main code for FedEx One Rate integration
Key Functions
_fedex_get_shipping_price_from_so:

Retrieves the shipping rate from FedEx based on the One Rate service.
Sets the shipping rate in the cost field (delivery_cost) on the order instead of using it as a customer-facing price.
_prepare_fedex_payload:

Constructs the API payload for FedEx, supporting:
Saturday Delivery: Set to True if the order is placed on Thursday.
Overnight Upgrade: Sets the service to Priority Overnight if the destination is within 150 miles, otherwise defaults to FedEx Express Saver.
_calculate_distance:

Placeholder function that estimates the distance between the warehouse and the delivery address.
In this setup, an approximate distance formula is used, which can be replaced with a third-party API (e.g., Google Maps API) for precise calculations.
_extract_one_rate:

Parses the FedEx API response to retrieve the One Rate shipping cost.
Looks for the TotalNetCharge in the response and sets it as the shipping cost on the order.
_fedex_create_shipment:

Creates the shipment with FedEx and stores the One Rate cost in the delivery_cost field on the delivery order.
Additional shipment details can be added here based on FedEx API requirements.
Testing the Module
Set Up Test Scenarios:

Saturday Delivery: Place an order on a Thursday to verify that the Saturday delivery option is enabled in the payload.
Overnight Upgrade: Test the distance calculation with a destination within 150 miles to ensure the service is upgraded to Priority Overnight.
Confirm Cost Field Update:

Check that the delivery_cost field on orders is populated with the correct rate from FedEx.
Verify that this rate is not affecting the customer-facing price.
Verify FedEx Responses:

Use logging (_logger.info) to confirm that Saturday delivery and overnight options are correctly included in the FedEx payload and that the response is parsed accurately.
Limitations and Notes
Distance Calculation: The _calculate_distance method currently uses a placeholder calculation. For real-world use, consider integrating a geocoding API (e.g., Google Maps) to get accurate distances for overnight eligibility.
Saturday Delivery Availability: FedEx’s actual Saturday delivery availability may vary by location. Ensure that this option is only used where applicable.
FedEx One Rate Eligibility: Make sure to configure eligible packaging types that align with FedEx One Rate offerings to avoid API errors.