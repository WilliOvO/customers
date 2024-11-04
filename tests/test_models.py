######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Customer Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Customer, DataValidationError, db
from .factories import CustomerFactory, BadCustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/customers"


######################################################################
#  Customer   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomer(TestCase):
    """Test Cases for Customer Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    # C U S T O M E R   T E S T   C A S E S
    ######################################################################

    def test_repr(self):
        """It should return customer name and id"""
        customer = CustomerFactory()
        customer.create()
        test = customer.__repr__()
        self.assertEqual(test, f"<Customer {customer.name} id=[{customer.id}]>")

    def test_create_customer(self):
        """It should create a Customer"""
        customer = CustomerFactory()
        customer.create()
        self.assertIsNotNone(customer.id)
        found = Customer.all()
        self.assertEqual(len(found), 1)
        data = Customer.find(customer.id)
        self.assertEqual(data.id, customer.id)
        self.assertEqual(data.name, customer.name)
        self.assertEqual(data.password, customer.password)
        self.assertEqual(data.address, customer.address)
        self.assertEqual(data.email, customer.email)
        self.assertEqual(data.active, customer.active)

        bad_customer = BadCustomerFactory()
        try:
            bad_customer.create()
        except DataValidationError:
            pass

    def test_read_a_customer(self):
        """It should Read a Customer"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        customer.create()
        self.assertIsNotNone(customer.id)
        # Fetch it back
        found_customer = Customer.find(customer.id)
        self.assertEqual(found_customer.id, customer.id)
        self.assertEqual(found_customer.name, customer.name)
        self.assertEqual(found_customer.password, customer.password)
        self.assertEqual(found_customer.email, customer.email)
        self.assertEqual(found_customer.address, customer.address)
        self.assertEqual(found_customer.active, customer.active)

    def test_update_a_customer(self):
        """It should Update a Customer"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        customer.create()
        logging.debug(customer)
        self.assertIsNotNone(customer.id)
        # Change it an save it
        customer.address = "123 Main St, Springfield, IL 62701"
        original_id = customer.id
        customer.update()
        self.assertEqual(customer.id, original_id)
        self.assertEqual(customer.address, "123 Main St, Springfield, IL 62701")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        customers = Customer.all()
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].id, original_id)
        self.assertEqual(customers[0].address, "123 Main St, Springfield, IL 62701")

        customer.active = "not a boolean"  # should not work
        try:
            customer.update()
        except DataValidationError:
            pass

    def test_update_no_id(self):
        """It should not Update a Customer with no id"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        self.assertRaises(DataValidationError, customer.update)

    def test_delete_a_customer(self):
        """It should Delete a Customer"""
        customer = CustomerFactory()
        customer.create()
        self.assertEqual(len(Customer.all()), 1)
        # delete the customer and make sure it isn't in the database
        customer.delete()
        self.assertEqual(len(Customer.all()), 0)

    @patch("service.models.db.session.commit")
    def test_delete_raises_exception(self, mock_delete):
        """It should raise an exception if delete fails"""
        mock_delete.side_effect = Exception()
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.delete)

    def test_list_all_customers(self):
        """It should List all Customers in the database"""
        customers = Customer.all()
        self.assertEqual(customers, [])
        # Create 5 customers
        for _ in range(5):
            customer = CustomerFactory()
            customer.create()
        # See if we get back 5 customers
        customers = Customer.all()
        self.assertEqual(len(customers), 5)

    def test_find_customer_by_name(self):
        """It should list all customers with the queried name"""
        customer = CustomerFactory()
        customer.create()
        found_customer = Customer.find_by_name(customer.name)
        self.assertEqual(customer.id, found_customer[0].id)

    def test_find_customer_by_email(self):
        """It should list all customers with the queried email"""
        customer = CustomerFactory()
        customer.create()
        found_customer = Customer.find_by_email(customer.email)
        self.assertEqual(customer.id, found_customer[0].id)

    def test_find_customer_by_address(self):
        """It should list all customers with the queried address"""
        customer = CustomerFactory()
        customer.create()
        found_customer = Customer.find_by_address(customer.address)
        self.assertEqual(customer.id, found_customer[0].id)

    def test_find_customer_by_active(self):
        """It should list all customers with the queried active status"""
        customer = CustomerFactory()
        customer.create()
        found_customer = Customer.find_by_active(customer.active)
        self.assertEqual(customer.id, found_customer[0].id)
