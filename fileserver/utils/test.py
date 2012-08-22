from django.test.simple import DjangoTestSuiteRunner

class FileServerTestSuiteRunner(DjangoTestSuiteRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        self.setup_test_environment()
        suite = self.build_suite(test_labels, extra_tests)
        #old_config = self.setup_databases()
        result = self.run_suite(suite)
        #self.teardown_databases(old_config)
        self.teardown_test_environment()
        return self.suite_result(suite, result)
