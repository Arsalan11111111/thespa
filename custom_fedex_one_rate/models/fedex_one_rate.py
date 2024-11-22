import requests
from odoo import models, fields, api
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    def _fedex_get_shipping_price_from_so(self, order):
        """
        Override this method to set the calculated shipping rate as the cost on the order.
        """
        try:
            # Prepare the payload with One Rate options and delivery enhancements
            payload = self._prepare_fedex_payload(order)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.fedex_api_key}',  # Replace with your actual FedEx API key
            }

            response = requests.post(
                "https://ws.fedex.com/web-services",  # Replace with production or sandbox URL as needed
                data=json.dumps(payload),
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                rate = self._extract_one_rate(data)
                
                # Instead of using it as price, set rate as the shipping cost on the order
                order.delivery_cost = rate  # Store rate in cost field

                # Return rate so it can be adjusted or used for customer-facing price
                return rate

            else:
                _logger.error(f"FedEx API error: {response.status_code} - {response.text}")
                raise UserError("Failed to retrieve shipping rate from FedEx.")

        except Exception as e:
            _logger.error(f"Error fetching FedEx One Rate: {e}")
            raise UserError("Error fetching FedEx One Rate.")

    def _prepare_fedex_payload(self, order):
        """
        Prepare the FedEx API request payload, including One Rate options, Saturday Delivery, 
        and distance-based upgrades for overnight shipping.
        """
        # Check if Saturday delivery is available (only if today is Thursday)
        saturday_delivery = False
        if fields.Date.context_today(self).weekday() == 3:  # Thursday
            saturday_delivery = True

        # Determine if the destination is within 150 miles for overnight upgrade
        # (This requires a calculation based on origin and destination coordinates)
        distance = self._calculate_distance(order.partner_shipping_id)
        if distance <= 150:
            service_type = "PRIORITY_OVERNIGHT"
        else:
            service_type = "FEDEX_EXPRESS_SAVER"

        fedex_package_type = 'YOUR_PACKAGING_TYPE'  # E.g., 'FEDEX_SMALL_BOX'

        payload = {
            "RequestedShipment": {
                "ShipTimestamp": fields.Datetime.now(),
                "DropoffType": "REGULAR_PICKUP",
                "ServiceType": service_type,
                "PackagingType": fedex_package_type,
                "Shipper": {
                    "Address": {
                        "PostalCode": "12345",
                        "CountryCode": "US"
                    }
                },
                "Recipient": {
                    "Address": {
                        "PostalCode": order.partner_shipping_id.zip,
                        "CountryCode": order.partner_shipping_id.country_id.code
                    }
                },
                "SpecialServicesRequested": {
                    "SpecialServiceTypes": "FEDEX_ONE_RATE",
                    "SaturdayDelivery": saturday_delivery
                },
                "RequestedPackageLineItems": [
                    {
                        "GroupPackageCount": 1,
                        "Weight": {
                            "Units": "LB",
                            "Value": sum(line.product_id.weight * line.product_uom_qty for line in order.order_line)
                        },
                        "Dimensions": {
                            "Length": 10,
                            "Width": 10,
                            "Height": 5
                        }
                    }
                ]
            }
        }
        return payload

    def _calculate_distance(self, partner):
        """
        Calculate the distance between the warehouse and the shipping address. 
        This is a placeholder and should be replaced with an actual distance calculation API.
        """
        # Example warehouse coordinates (replace with actual warehouse coordinates)
        warehouse_lat = 37.7749
        warehouse_long = -122.4194

        # Fetch coordinates for the shipping partner
        # Placeholder values; in practice, use a geocoding service
        partner_lat = 37.7749
        partner_long = -122.4194

        # Simple distance formula (or use a more accurate distance API)
        distance = ((warehouse_lat - partner_lat)**2 + (warehouse_long - partner_long)**2)**0.5
        return distance * 69  # Convert to miles (approximate conversion)

    def _extract_one_rate(self, data):
        """
        Extract the One Rate price from the FedEx response.
        """
        rate_detail = data.get('RateReplyDetails', [])
        if not rate_detail:
            raise UserError("No rate details found in FedEx response.")

        # Extract the One Rate price from response
        one_rate = rate_detail[0].get('RatedShipmentDetails', [])[0].get('ShipmentRateDetail', {}).get('TotalNetCharge', {}).get('Amount')
        
        if not one_rate:
            raise UserError("Failed to retrieve One Rate price from FedEx.")
        
        return one_rate

    def _fedex_create_shipment(self, picking):
        """
        Override to create a FedEx shipment and apply the cost rate.
        """
        rate = self._fedex_get_shipping_price_from_so(picking.sale_id)

        # Set rate as the cost directly on the picking or delivery order cost field
        picking.delivery_cost = rate  # Update cost here rather than price

        # Continue with creating the shipment as usual
        # The rest of this method would contain logic to create the shipment with FedEx API
