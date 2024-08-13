.. _websocket_consumers:

WebSocket Consumers And Celery
==============================

This section provides detailed documentation for the WebSocket consumers used in the Django project, describing their purpose, connection methods, actions, and parameters.

PickupRequestConsumer
---------------------

Handles the creation of pickup requests by customers and assigns them to the nearest available vendor.

**connect()**

**Description:** Establishes a WebSocket connection for authenticated users.

**Actions:**

- Sets the user's group name to ``pickup_{user.id}``.

- Accepts the connection.

- Adds the user's channel to the group.

**disconnect(close_code)**

**Description:** Handles the disconnection of the WebSocket.

**Actions:**

- Removes the user's channel from the group.


**receive(text_data)**

**Description:** Receives and processes messages from the WebSocket.

**Actions:**

- Parses the incoming JSON data.

- Calls the `create_pickup_request` method with the parsed data.

- Sends the result back to the WebSocket.

**create_pickup_request(data)**

**Description:** Creates a new pickup request and assigns it to the nearest active vendor.

**Parameters:** 

- **data**: JSON data containing latitude and longitude.

**Actions:**

- Retrieves the customer profile based on the authenticated user.

- Calls the Celery task `assign_vendor_task` to find the nearest vendor.

- Creates a `PickupRequest` and sends a notification to the assigned vendor.

- Returns the result, including the pickup request details or an error message.

RejectAndReassignPickupRequestConsumer
--------------------------------------

Handles the rejection of pickup requests by vendors and reassigns them to the next nearest available vendor.

**connect()**

**Description:** Establishes a WebSocket connection for authenticated users.

**Actions:**

- Sets the user's group name to ``rejectandreassign_{user.id}``.

- Accepts the connection.

- Adds the user's channel to the group.

**disconnect(close_code)**

**Description:** Handles the disconnection of the WebSocket.

**Actions:**
- Removes the user's channel from the group.

**receive(text_data)**

**Description:** Receives and processes messages from the WebSocket.

**Actions:**

- Parses the incoming JSON data.

- Calls the `reject_and_reassign_pickup_request` method with the parsed data.

- Sends the result back to the WebSocket.

**reject_and_reassign_pickup_request(data)**

**Description:** Rejects the current pickup request and assigns it to the next nearest available vendor.

**Parameters:**

- **data**: JSON data containing pickup request ID.

**Actions:**

- Retrieves the vendor profile based on the authenticated user.

- Marks the current pickup request as rejected and adds the vendor to the rejected vendors list.

- Calls the Celery task `assign_vendor_task` to find the next nearest vendor.

- Updates the pickup request with the new vendor and sends notifications.

- Returns the result, including the updated pickup request details or an error message.

UpdatePickupRequestStatusConsumer
---------------------------------

Handles the updating of pickup request status by vendors.

**connect()**

**Description:** Establishes a WebSocket connection for authenticated users.

**Actions:**

- Sets the user's group name to ``updatepickup_{user.id}``.

- Accepts the connection.

- Adds the user's channel to the group.

**disconnect(close_code)**

**Description:** Handles the disconnection of the WebSocket.

**Actions:**

- Removes the user's channel from the group.

**receive(text_data)**

**Description:** Receives and processes messages from the WebSocket.

**Actions:**

- Parses the incoming JSON data.

- Calls the `update_pickup_request_status` method with the parsed data.

- Sends the result back to the WebSocket.

**update_pickup_request_status(data)**

**Description:** Updates the status of a pickup request.

**Parameters:**

- **data**: JSON data containing pickup request ID and new status.

**Actions:**

- Retrieves the vendor and pickup request based on the authenticated user and provided ID.

- Updates the status of the pickup request and sends a notification to the customer if accepted.

- Returns the result, including the updated pickup request status or an error message.

CustomerRejectPickupRequestConsumer
-----------------------------------

Handles the rejection of pickup requests by customers.

**connect()**

**Description:** Establishes a WebSocket connection for authenticated users.

**Actions:**

- Sets the user's group name to ``customerReject_{user.id}``.

- Accepts the connection.

- Adds the user's channel to the group.

**disconnect(close_code)**

**Description:** Handles the disconnection of the WebSocket.

**Actions:**

- Removes the user's channel from the group.

**receive(text_data)**

**Description:** Receives and processes messages from the WebSocket.

**Actions:**

- Parses the incoming JSON data.

- Calls the `customer_reject_pickup_request` method with the parsed data.

- Sends the result back to the WebSocket.

**customer_reject_pickup_request(data)**

**Description:** Rejects a pickup request by a customer.

**Parameters:**

- **data**: JSON data containing pickup request ID and remarks.

**Actions:**

- Retrieves the customer profile based on the authenticated user.

- Marks the pickup request as rejected and updates it with remarks.

- Sends a notification to the vendor about the rejection.

- Returns the result, including the rejection status or an error message.

NotificationConsumer
---------------------

Handles the sending of notifications to users.

**connect()**

**Description:** Establishes a WebSocket connection for authenticated users.

**Actions:**

- Sets the user's group name to ``Notifications_{user.id}``.

- Accepts the connection.

- Adds the user's channel to the group.

- Logs the connection event.

**disconnect(close_code)**

**Description:** Handles the disconnection of the WebSocket.

**Actions:**

- Removes the user's channel from the group.

- Logs the disconnection event.

**receive(text_data)**

**Description:** Receives messages from the WebSocket.

**send_notification(event)**

**Description:** Sends notifications to the user.

**Parameters:**

- **event**: Dictionary containing the message to be sent.

**Actions:**

- Logs the sending event.

- Sends the message to the WebSocket.

WebSocket Routing
-----------------

This section defines the WebSocket routes for the consumers.

**websocket_urlpatterns**

- **Route for notifications**

  - **Path**: ``ws/notifications/``

  - **Consumer**: `NotificationConsumer`

- **Route for updating pickup request status**

  - **Path**: ``ws/update_pickup_request_status/``

  - **Consumer**: `UpdatePickupRequestStatusConsumer`

- **Route for rejecting and reassigning pickup requests**

  - **Path**: ``ws/reject_and_reassign_pickup_request/``

  - **Consumer**: `RejectAndReassignPickupRequestConsumer`

- **Route for rejecting pickup requests by customers**

  - **Path**: ``ws/customer_reject_pickup_request/``

  - **Consumer**: `CustomerRejectPickupRequestConsumer`

- **Route for creating pickup requests**

  - **Path**: ``ws/pickup_request/``

  - **Consumer**: `PickupRequestConsumer`

Celery Tasks
------------

This section defines the asynchronous tasks used for notifications and vendor assignment.

**send_notification_task**

**Description:** Sends notifications to users.

**Parameters:**

- **user_id**: ID of the user to send the notification to.

- **message**: The message content to be sent.

**Actions:**

- Logs the sending event.

- Uses the channel layer to send the notification to the user's group.

- Logs success or error.

**assign_vendor_task**

**Description:** Assigns the nearest available vendor to a pickup request.

**Parameters:**

- **customer_id**: ID of the customer requesting the pickup.

- **latitude**: Latitude of the pickup location.

- **longitude**: Longitude of the pickup location.

- **excluded_vendor_ids**: List of vendor IDs to exclude from assignment.

**Actions:**

- Retrieves the customer profile.

- Finds the nearest active vendor excluding the provided IDs.

- Returns the nearest vendor's ID or `None` if no vendor is found.

Usage
-----

   **Demo Video**

   The following video demonstrates how to connect the WebSocket consumers and Celery in the project:

   .. raw:: html

      <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; height: auto;">
      <iframe src="https://www.loom.com/embed/06bf24cf527b407493fcd164db8e376b?sid=d0248dd2-63b0-4705-b095-cec42395195b" 
               frameborder="0" 
               webkitallowfullscreen 
               mozallowfullscreen 
               allowfullscreen 
               style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
      </iframe>
      </div>


WebSocket Consumers
-------------------

The WebSocket consumers handle various real-time interactions, such as creating pickup requests, updating pickup statuses, rejecting requests, and sending notifications. To use the WebSocket consumers effectively, follow these steps:

1. **Set Up Redis and RabbitMQ**

   WebSocket consumers require a message broker for real-time communication. You can set up Redis and RabbitMQ using Docker.

   - **Running Redis in Docker**:

     Redis serves as the message broker that the Django Channels layer interacts with. Start a Redis container using the following command:

     .. code-block:: sh

        docker run -d -p 6379:6379 redis

     This command pulls the Redis image (if not already available), runs it in detached mode, and maps the default Redis port 6379.

   - **Running RabbitMQ in Docker**:

     RabbitMQ is another option for message brokering, especially when working with Celery. Start RabbitMQ with its management interface enabled using the following command:

     .. code-block:: sh

        docker run -it -d --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management

     This command starts RabbitMQ and exposes the ports for messaging (5672) and the management dashboard (15672).

2. **Configure Django Channels**

   Ensure your Django application is configured to use Channels with Redis as the backend. Update your `settings.py` to include Channels configurations.

   .. code-block:: sh

       CHANNEL_LAYERS = {
       'default': {
          'BACKEND': 'channels_redis.core.RedisChannelLayer',
          'CONFIG': {
              "hosts": [('127.0.0.1', 6379)],
          },
        },
        }




3. **Run the Django Development Server**

   Once Redis and RabbitMQ are running, start your Django development server to enable WebSocket connections:

   .. code-block:: sh

       uvicorn trashapi.asgi:application --port 8000 --log-level debug --reload

4. **Testing WebSocket Endpoints**

   WebSocket endpoints can be tested using tools like Postman, Thunder Client, or directly in your application. Each WebSocket consumer handles specific events as defined in the documentation. Ensure that your WebSocket client connects to the appropriate endpoint and sends messages in the expected JSON format.

Celery
------

Celery is used for handling background tasks such as assigning vendors to pickup requests and sending notifications asynchronously. Follow these steps to set up and use Celery:

1. **Install Required Dependencies**

   Ensure that Celery, Django_celery_results, Redis, and RabbitMQ are installed and properly configured in your Django project.

2. **Configure Django Celery results**

   Ensure your Django application is configured to use Django_celery_results as the backend. Update your `settings.py` to include Celery configurations.

   .. code-block:: sh

       CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

       CELERY_RESULT_BACKEND = 'django-cache'


       CELERY_CACHE_BACKEND = 'default'

       CACHES = {
         'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'my_cache_table',
         }
       }

   Run the following script to setup 'my_cache_table'

   .. code-block:: sh

       python manage.py createcachetable



3. **Running Celery Workers**

   Start Celery workers to handle background tasks. The commands vary based on the operating system:

   - **For Windows**:

     .. code-block:: sh

        celery -A trashapi worker --loglevel=info -P solo

     This command starts a Celery worker in a Windows environment with the `solo` pool, necessary due to multiprocessing limitations on Windows.

   - **For Linux**:

     .. code-block:: sh

        celery -A trashapi worker -l info

     On Linux, Celery workers can be started with the default multiprocessing pool, providing better performance and scalability.

4. **Monitoring Celery with Flower**

   Flower is a real-time web-based monitor for Celery. You can run it alongside your Celery workers to monitor task progress and health.

   - **Starting Flower**:

       .. code-block:: sh

          celery -A trashapi flower


     Access Flower's dashboard at `http://localhost:5555` to monitor tasks, workers, and queues.

5. **Using Celery in Django**

   Once the workers are running, Celery tasks like `send_notification_task` and `assign_vendor_task` will be executed asynchronously based on the events triggered by the WebSocket consumers. This ensures that time-consuming tasks do not block the main application flow.

6. **Shutting Down Workers**

   When done with testing or running your application, stop the Celery workers and Flower monitor gracefully using `CTRL + C` in the terminal where they are running.
