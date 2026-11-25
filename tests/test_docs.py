"""Tests of documentation data/validators only; not application acceptance tests."""
import copy
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from scripts.check_docs import allocation_valid, inventory_valid, verify_demo, check_catalog, check_links, validate_all
from scripts.build_reference import generate

ROOT=Path(__file__).resolve().parents[1]

class DocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo=json.loads((ROOT/'examples/demo-order.json').read_text(encoding='utf-8'))
        cls.catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
        cls.api_schema=json.loads((ROOT/'schemas/api-models.schema.json').read_text(encoding='utf-8'))

    def test_full_repository(self):
        self.assertEqual(validate_all()['status'],'passed')

    def test_generated_references_match(self):
        for name,text in generate().items():
            self.assertEqual((ROOT/name).read_text(encoding='utf-8'),text,name)

    def test_internal_links(self):
        self.assertGreater(check_links(ROOT),100)

    def test_catalog_counts(self):
        self.assertEqual(check_catalog(self.catalog)['example_mentions'],3840)

    def test_duplicate_category_rejected(self):
        c=copy.deepcopy(self.catalog)
        c['categories'][1]['id']=c['categories'][0]['id']
        with self.assertRaises(AssertionError):check_catalog(c)

    def test_invalid_category_parent_rejected(self):
        c=copy.deepcopy(self.catalog)
        c['categories'][0]['children'][0]['id']='99.01'
        with self.assertRaises(AssertionError):check_catalog(c)

    def test_demo_totals(self):
        self.assertEqual(verify_demo(self.demo)['contribution'],'5200.00')

    def test_wrong_order_total_rejected(self):
        d=copy.deepcopy(self.demo);d['order_total']='12801.00'
        with self.assertRaises(AssertionError):verify_demo(d)

    def test_over_shipment_rejected(self):
        d=copy.deepcopy(self.demo);d['shipments'][1]='601'
        with self.assertRaises(AssertionError):verify_demo(d)

    def test_fee_mismatch_rejected(self):
        d=copy.deepcopy(self.demo);d['payments'][0]['fee']='16.00'
        with self.assertRaises(AssertionError):verify_demo(d)

    def test_zero_exchange_rate_rejected(self):
        d=copy.deepcopy(self.demo);d['fx']['rate']='0'
        with self.assertRaises(AssertionError):verify_demo(d)

    def test_unknown_currency_rejected(self):
        d=copy.deepcopy(self.demo);d['costs'][0]['currency']='JPY'
        with self.assertRaises(AssertionError):verify_demo(d)

    def test_valid_inventory_partition(self):
        self.assertTrue(inventory_valid({'on_hand':'10','reserved':'8','blocked':'2'}))

    def test_inventory_overcommit_rejected(self):
        self.assertFalse(inventory_valid({'on_hand':'10','reserved':'8','blocked':'3'}))

    def test_negative_inventory_rejected(self):
        self.assertFalse(inventory_valid({'on_hand':'-1','reserved':'0','blocked':'0'}))

    def test_valid_allocation(self):
        self.assertTrue(allocation_valid('100','80','80'))

    def test_over_allocation_rejected(self):
        self.assertFalse(allocation_valid('100','80','81'))

    def test_zero_allocation_rejected(self):
        self.assertFalse(allocation_valid('100','80','0'))

    def test_customer_schema(self):
        v=Draft202012Validator({**self.api_schema,'$ref':'#/$defs/CustomerCreate'},format_checker=FormatChecker())
        v.validate({'company_name':'Example Buyer','country_code':'US','contact_email':'buyer@example.com'})

    def test_client_tenant_field_rejected(self):
        v=Draft202012Validator({**self.api_schema,'$ref':'#/$defs/CustomerCreate'})
        with self.assertRaises(ValidationError):
            v.validate({'company_name':'Example Buyer','country_code':'US','tenant_id':'client-selected'})

    def test_bad_email_rejected(self):
        v=Draft202012Validator({**self.api_schema,'$ref':'#/$defs/CustomerCreate'},format_checker=FormatChecker())
        with self.assertRaises(ValidationError):
            v.validate({'company_name':'Example Buyer','country_code':'US','contact_email':'not-an-email'})

    def test_zero_quantity_schema_rejected(self):
        v=Draft202012Validator({**self.api_schema,'$ref':'#/$defs/ReservationCreate'})
        with self.assertRaises(ValidationError):
            v.validate({'order_line_id':'10000000-0000-4000-8000-000000000001','stock_lot_id':'20000000-0000-4000-8000-000000000001','quantity':'0'})

    def test_no_fabricated_business_test_results(self):
        tests=json.loads((ROOT/'data/acceptance-tests.json').read_text(encoding='utf-8'))['tests']
        self.assertEqual(len(tests),72)
        self.assertTrue(all(t['status']=='designed' and t['actual_result'] is None for t in tests))

    def test_state_machines_require_guard(self):
        data=json.loads((ROOT/'data/state-machines.json').read_text(encoding='utf-8'))['machines']
        self.assertTrue(all(transition[3] for machine in data.values() for transition in machine['transitions']))

if __name__=='__main__':unittest.main()
