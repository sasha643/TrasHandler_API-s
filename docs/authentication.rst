Mobile Number Backend Authentication
====================================

**Description:**
Custom authentication backend that allows users to authenticate using their mobile number. This backend checks if the user exists and returns the appropriate user profile (either `CustomerAuth` or `VendorAuth`).

**Methods:**

1. **authenticate(request, mobile_no=None, \*\*kwargs):**

   **Description:**
   - Authenticates a user based on their mobile number.

   **Parameters:**

   - `request` (`HttpRequest`): The request object.

   - `mobile_no` (`str`): The mobile number provided for authentication.

   - `\*\*kwargs` (`dict`): Additional keyword arguments.

   **Actions:**

   - Retrieves the user based on the provided mobile number.

   - Checks if the user has a `CustomerAuth` or `VendorAuth` profile and returns the appropriate profile.

   - Returns `None` if the user does not exist or does not have a profile.

   **Behavior:**

   - If the mobile number is `None`, the method returns `None`.

   - The method attempts to retrieve the user based on the provided mobile number and checks for the presence of `CustomerAuth` or `VendorAuth`.

   - If neither profile is found, the method returns `None`.

2. **get_user(user_id):**

   **Description:**
   - Retrieves a user by their ID.

   **Parameters:**

   - `user_id` (`int`): The ID of the user.

   **Actions:**

   - Returns the user if found, otherwise returns `None`.

   **Behavior:**

   - The method attempts to retrieve the user based on the provided user ID.

   - If the user does not exist, it returns `None`.
