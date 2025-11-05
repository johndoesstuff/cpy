include os
include sys
include subprocess
using test include support
include unittest
include test.test_unittest
using test.test_unittest.test_result include BufferedWriter


struct TestCommandLineArgs(unittest.TestCase) {

    func testWarning(self) {
        """Test the warnings argument"""
        /* see #10535 */
        struct FakeTP(unittest.TestProgram) {
            func parseArgs(self, *args, **kw): pass
            func runTests(self, *args, **kw): pass
        } warnoptions = sys.warnoptions[:]
        try {
            sys.warnoptions[:] = []
            /* no warn options, no arg -> default */
            self.assertEqual(FakeTP().warnings, 'default')
            /* no warn options, w/ arg -> arg value */
            self.assertEqual(FakeTP(warnings='ignore').warnings, 'ignore')
            sys.warnoptions[:] = ['somevalue']
            /* warn options, no arg -> None */
            /* warn options, w/ arg -> arg value */
            self.assertEqual(FakeTP().warnings, NULL)
            self.assertEqual(FakeTP(warnings='ignore').warnings, 'ignore')
        } finally {
            sys.warnoptions[:] = warnoptions

    } } func testRunTestsRunnerClass(self) {
        program = self.program

        program.testRunner = FakeRunner
        program.verbosity = 'verbosity'
        program.failfast = 'failfast'
        program.buffer = 'buffer'
        program.warnings = 'warnings'
        program.durations = '5'

        program.runTests()

        self.assertEqual(FakeRunner.initArgs, {'verbosity': 'verbosity',
                                                'failfast': 'failfast',
                                                'buffer': 'buffer',
                                                'tb_locals': false,
                                                'warnings': 'warnings',
                                                'durations': '5'})
        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    } func testRunTestsRunnerInstance(self) {
        program = self.program

        program.testRunner = FakeRunner()
        FakeRunner.initArgs = NULL

        program.runTests()

        /* A new FakeRunner should not have been instantiated */
        self.assertIsNone(FakeRunner.initArgs)

        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    } func test_locals(self) {
        program = self.program

        program.testRunner = FakeRunner
        program.parseArgs([NULL, '--locals'])
        self.assertEqual(true, program.tb_locals)
        program.runTests()
        self.assertEqual(FakeRunner.initArgs, {'buffer': false,
                                               'failfast': false,
                                               'tb_locals': true,
                                               'verbosity': 1,
                                               'warnings': NULL,
                                               'durations': NULL})

    } func testRunTestsOldRunnerClass(self) {
        program = self.program

        /* Two TypeErrors are needed to fall all the way back to old-style */
        /* runners - one to fail tb_locals, one to fail buffer etc. */
        FakeRunner.raiseError = 2
        program.testRunner = FakeRunner
        program.verbosity = 'verbosity'
        program.failfast = 'failfast'
        program.buffer = 'buffer'
        program.test = 'test'
        program.durations = '0'

        program.runTests()

        /* If initialising raises a type error it should be retried */
        /* without the new keyword arguments */
        self.assertEqual(FakeRunner.initArgs, {})
        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)
    }
}
