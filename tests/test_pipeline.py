import unittest, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
import generate_data
from pipeline import run_pipeline

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generate_data.main(); cls.result=run_pipeline()
    def test_orders_exist(self): self.assertGreater(self.result["orders"],0)
    def test_revenue_positive(self): self.assertGreater(self.result["revenue"],0)
    def test_outputs_exist(self):
        for name in ["daily_sales.csv","customer_summary.csv","funnel_summary.csv"]:
            self.assertTrue((ROOT/"data"/"output"/name).exists())

if __name__=="__main__": unittest.main()
