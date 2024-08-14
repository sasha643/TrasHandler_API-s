.. _api_endpoints:

API Endpoints
=============

This section provides a detailed description of the URL patterns and the expected payloads for various API endpoints in the TrasHandler. The examples include payload structures for both requests and responses.

Admin and Schema Documentation
------------------------------

   **Endpoint:** `/admin/`

   **Method:** `GET`

   **Admin site**

   **Purpose:** Access the Django admin interface.

   **Endpoint:** `/api/schema/`

   **Method:** `GET`

   **API schema**

   **Purpose:** Access the API schema documentation.

   **Endpoint:** `/api/docs/`

   **Method:** `GET`

   **API documentation**

   **Purpose:** Access the API documentation.


Authentication and Registration
-------------------------------

   **Endpoint:** `/api/auth/customer/register/`

   **Method:** `POST`

   **Customer Registration**

   **Request Payload:**

   .. code-block:: json

      {
        "name": "John",
        "mobile_number": "1234567890",
        "email": "john.doe@example.com"
      }

   **Response:**

   .. code-block:: json

      {
        "name": "John",
        "mobile_number": "1234567890",
        "email": "john.doe@example.com",
      }


   **Endpoint:** `/api/auth/vendor/register/`

   **Method:** `POST`

   **Vendor Registration**

   **Request Payload:**

   .. code-block:: json

      {
        "name": "Doe",
        "mobile_number": "1234567890",
        "email": "vendor@example.com"
      }

   **Response:**

   .. code-block:: json

      {
        "name": "Doe",
        "mobile_number": "1234567890",
        "email": "vendor@example.com",

      }


   **Endpoint:** `/customersignin/`

   **Method:** `POST`

   **Customer Login**

   **Request Payload:**

   .. code-block:: json

      {
        "mobile_number": "1234567890"
      }

   **Response:**

   .. code-block:: json

      {
        "token": "jwt_token_here"
      }


   **Endpoint:** `/vendorsignin/`

   **Method:** `POST`

   **Vendor Login**

   **Request Payload:**

   .. code-block:: json

      {
        "mobile_number": "1234567890"
      }

   **Response:**

   .. code-block:: json

      {
        "token": "jwt_token_here"
      }

Profile and Location Management
-------------------------------


   **Endpoint:** `/vendor/profile/<int:vendor_id>/`

   **Method:** `GET`

   **Vendor Profile Details**

   **Response:**

   .. code-block:: json

      {

        "business_name": "Doe Enterprises",
      }


   **Endpoint:** `/vendor/pickup-requests/<int:vendor_id>/`

   **Method:** `GET`

   **Vendor Pickup Requests**

   **Response:**

   .. code-block:: json

      {
        "pickup_requests": [
          {
            "customer_id": 1,
            "pickup_request_id": 2,
            "customer_name": "John Doe",
            "customer_mobile_no": 697967590,
            "latitude": 30.0,
            "longitude": 27.0,
            "status": "pending",
            "remarks": ""
          }
        ]
      }


   **Endpoint:** `/customer/<int:customer_id>/pickup-request/`

   **Method:** `GET`

   **Customer Pickup Request**

   **Response:**

   .. code-block:: json

      {
        "pickup_request_id": 1,      
        "vendor_details": {
          "vendor_name": "Doe Enterprises",
          "vendor_mobile_no": "123098876",

        }
      }
