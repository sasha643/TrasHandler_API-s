JWT Authentication Middleware
=============================

**Description:**
Custom middleware that handles JWT authentication for WebSocket connections. It validates the token, decodes it, and attaches the authenticated user to the connection scope.

**Methods:**

1. **get_user(validated_token):**

   **Description:**
   - Retrieves a user based on the validated JWT token.

   **Parameters:**

   - `validated_token` (`dict`): The decoded JWT token containing the `user_id`.

   **Actions:**

   - Attempts to retrieve the user from the database using the `user_id`.

   - Returns the user if found, or `AnonymousUser` if the user does not exist.

   **Behavior:**

   - The method uses the `database_sync_to_async` decorator to ensure it can run asynchronously within an async context.

2. **JwtAuthMiddleware(BaseMiddleware):**

   **Description:**
   - Middleware class that processes WebSocket connections to authenticate users via JWT tokens.

   **Actions:**

   - Closes old database connections to prevent usage of timed-out connections.

   - Extracts the JWT token from the WebSocket connection's query string.

   - Validates and decodes the token using `UntypedToken`.

   - If the token is valid, it retrieves the user and attaches them to the connection scope.

   **Behavior:**

   - If the token is invalid, the connection is not authenticated, and the method returns `None`.

   - If the token is valid, the decoded data is used to retrieve the user, who is then attached to the WebSocket scope.

3. **JwtAuthMiddlewareStack(inner):**

   **Description:**
   - A helper function that creates a middleware stack, integrating `JwtAuthMiddleware` with the Django `AuthMiddlewareStack`.

   **Actions:**

   - Wraps the provided `inner` application with the `JwtAuthMiddleware` to handle JWT authentication.
