# Computer Science Course Management Platform

## Description

The premise for CSCMP is that the above procedures can be made more efficient, most tangibly from the professor’s/grader’s perspective. With CSCMP, the grader doesn’t download files to screen or run tests against. Instead, the student runs the tests via CSCMP (remotely) and any submitted code have a test result associated with it. The professor, then, will have all assignment submissions available in the remote repository, where they can view the source code as well as the test results of any given submission. This means that there will be no need to for a grader to download any files and run them locally.

## Motivation

The current system used at Colorado College for CS assignment management is as follows:

* Professors of Computer Science at Colorado College uses Canvas for course management
* While Canvas offers many functionalities that are useful also for programming courses (keeping track of grades, discussion boards, messaging, etc.), it offers no support for automated and integrated assignment assessment
* The current procedure for assignment assessment is (in broad strokes and to the best of our knowledge) as follows:
* Grader (which may be a professor or an appointed student) logs in to Canvas and navigates through the user interface to assignment page.
* Grader downloads, for each student, the source files to their machine
* They run the code, potentially against some test file, and they screen the code to judge its quality

From student's perspective:

* Student navigates the Canvas interface to assignment page, downloads to their machine necessary starter files (this typically includes assignment description, set up code, and test code)
* Student writes the code necessary to complete the assignment, and runs potential tests locally on their machine
* When student is happy with the source files, they go on to assignment page and submits relevant files (the format of submitted product vary depending on professor; some require the files that were created/edited by student while others want the whole project directory as a compressed file)
