# Derp User Stories

This document is intended to describe an experience that someone using a product should have when using the project.

A verbal description and justification of what the program should support.

End users: Student, professor, administrator/site maintainence, graders, paraprofs

## Professor

A professor is someone who will be in charge of teaching classes.

A professor goes to the website. A splash page is shown which will allow them to log in or sign up.
They can click the sign-in, which will redirect to SSI at Colorado College. 
(For open source-purposes, a password tool will also be provided. This will be configurable via `CONFIG.py`).

The professor will use one of the sign-in options and create an account.
An administrator of the site will be able to set their status to professor, such that they will be able to:

 - Log in normally using the feature they first signed in with,
 - Create courses
 - Add students to courses (?)
 - Create assignments within courses
 - Create tests which rely on code templates, and have those tests run automatically on submitted code. (?)
 - View/download student submissions, either through the portal or with some sort of API tool.


## User

A user is an individual capable of taking a class as a student.

Users sign-up and log-in using the same methods that professors use (via SSI or passwords).

 - Users must be able to be enrolled in a class by a professor (?)
 - User wants to submit code to an assignment
 - User must be able to run tests on their code at any time in order to evaluate a potential submission.
 - Tests should test the output of the code and not code quality
 
## Administrator

Someone needs to be able to set up this piece of software in order to work.

We will provide documentation about how to run this piece of software, for other companies/schools to be able to run this piece of software.
