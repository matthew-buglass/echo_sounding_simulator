import unittest

from utils.error_pipeline import ErrorType, Noise, run_pipeline


class TestErrorType(unittest.TestCase):
    def test_instantiating_generic_raises_type_error(self):
        self.assertRaises(TypeError, ErrorType)

    def test_instantiating_incomplete_error_type_raises_type_error(self):
        class BadError(ErrorType):
            def __init__(self, *args, **kwargs):
                super().__init__(self, *args, **kwargs)

        self.assertRaises(TypeError, BadError)


class TestNoiseErrorType(unittest.TestCase):
    def test_calling_on_five_percent_error_calculates_vector_correctly(self):
        seeds = [0, 10, 304597]
        expected_vectors = [(0, 0, 1.0344421851525047), (0, 0, 1.0071402594689913), (0, 0, 0.9884574295419192)]
        err = Noise(0.05)
        vector = (0, 0, 1)

        for i, seed in enumerate(seeds):
            new_vector = err.eval(vector, seed)

            # vector is correct and error is within 5%
            self.assertTrue(abs(vector[2] - new_vector[2]) / vector[2] <= 0.05, msg="Error not within 5%")
            self.assertTupleEqual(new_vector, expected_vectors[i], msg="Vectors not equal")


class TestRunPipeline(unittest.TestCase):
    def test_with_empty_pipeline_yields_identical_vector(self):
        errors = []
        start_vector = (0, 0, 1)
        expected_vector = (0.0, 0.0, 1.0)

        new_vector = run_pipeline(errors, start_vector)

        self.assertEqual(3, len(new_vector))
        self.assertAlmostEqual(expected_vector[0], new_vector[0])
        self.assertAlmostEqual(expected_vector[1], new_vector[1])
        self.assertAlmostEqual(expected_vector[2], new_vector[2])

    def test_with_one_noise_pipeline_step_yields_correct_vector(self):
        errors = [Noise(0.05)]
        seed = 304597
        start_vector = (0, 0, 1)
        expected_vector = (0.0, 0.0, 0.9884574295419192)

        new_vector = run_pipeline(errors, start_vector, seed=seed)

        self.assertEqual(3, len(new_vector))
        self.assertAlmostEqual(expected_vector[0], new_vector[0])
        self.assertAlmostEqual(expected_vector[1], new_vector[1])
        self.assertAlmostEqual(expected_vector[2], new_vector[2])

    def test_with_multiple_noise_pipeline_steps_yields_correct_vector(self):
        errors = [Noise(0.05), Noise(0.01), Noise(0.10)]
        seed = 1238987523
        start_vector = (0, 0, 1)
        expected_vector = (0.0, 0.0, 0.9670810794357534)

        new_vector = run_pipeline(errors, start_vector, seed=seed)

        self.assertEqual(3, len(new_vector))
        self.assertAlmostEqual(expected_vector[0], new_vector[0])
        self.assertAlmostEqual(expected_vector[1], new_vector[1])
        self.assertAlmostEqual(expected_vector[2], new_vector[2])


if __name__ == '__main__':
    unittest.main()
