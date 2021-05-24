Outline of Henry's software

Part Null:
  -- Spend time exploring this part of the system, and write posibilities of how a change in database could improve the operations of other parts of the system.
  -- In a lot of ways the complexity of connecting to sharepoint and exce is the source of the complexity of the system overall.
    1. A sharepoint list that is loaded with the client information from Henry Ford Hospital.

Part I.
    1. Gets delivery information from sharepoint list
    2. Does basic validation/correction of that information
    3. Creates dir structure that organizes the information
        a. This breaks deliveries down by AM, PM, Covenant and 

Part II.
    1. Bringfood.care creates routes from output of Part I.

Part III.
    1. Relates the delivery information to the menu information, and packages it into a coherent datastructure.
    2. Generates various views of that datastructure to aid in the task of box preparation and delivery.

        a. Fulfillment Tickets
        b. Pick Lists
        c. Delivery Route Lists
        d. Delivery interface

Part IV.
    1. Provides an interface for drivers to interact with the delivery data, marking as complete or failed, and noting reason for failed delivery.