import unittest

from utils.error_pipeline import ErrorType, Noise


class TestErrorType(unittest.TestCase):
    def test_calling_eval_on_generic_raises_type_error(self):
        self.assertRaises(TypeError, ErrorType)


class TestNoiseErrorType(unittest.TestCase):
    def test_calling_on_five_percent_error_calculates_vector_correctly(self):
        seeds = [0, 10, 304597]
        expected_vectors = [(0, 0, 1.0344421851525047), (0, 0, 1.0071402594689913), (0, 0, 0.9884574295419192)]
        err = Noise(0.05)
        vector = (0, 0, 1)

        for i, seed in enumerate(seeds):
            new_vector = err.eval(vector, seed)

            # vector is correct and error is within 5%
            self.assertTrue(abs(vector[2]-new_vector[2])/vector[2] <= 0.05, msg="Error not within 5%")
            self.assertTupleEqual(new_vector, expected_vectors[i], msg="Vectors not equal")




if __name__ == '__main__':
    unittest.main()
