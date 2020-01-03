import unittest
import sys


if not sys.platform.startswith('linux'):   #no python bindings available for other languages
    print("Skipping ViennaRNA Python bindings test since detected OS is not Linux")
else:
    import RNA
    from oracle import vienna

    #because this class is tightly coupled with the Python bindings,
    # much of the testing will be conducted as integration tests

    class TestVienna(unittest.TestCase):
        TEMPERATURE = 41.2

        def setUp(self):
            self.oracle = vienna.Oracle(self.TEMPERATURE)

        def test_init_temperature(self):
            self.assertEqual(RNA.cvar.temperature, self.TEMPERATURE)

        def test_set_temperature(self):
            ALTERNATE_TEMPERATURE = 52.7
            self.oracle.set_temperature(ALTERNATE_TEMPERATURE)
            self.assertEqual(RNA.cvar.temperature, ALTERNATE_TEMPERATURE)

        def test_init_params_filename(self):
            TEST_FILENAME = "dna_mathews2004.par"
            self.oracle = vienna.Oracle(self.TEMPERATURE, params_filename=f"lib/{TEST_FILENAME}")
            self.assertEqual(TEST_FILENAME, RNA.param().param_file)
