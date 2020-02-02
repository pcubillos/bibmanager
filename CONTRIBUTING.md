Contributing
============

Feel free to contribute to this repository by submitting code pull
requests, raising issues, or emailing the administrator directly.

Raising Issues
--------------

Whenever you want to raise a new issue, make sure that it has not
already been mentioned in the issues list.  If an issue exists, consider
adding a comment if you have extra information that further describes
the issue or may help to solve it.

If you are reporting a bug, make sure to be fully descriptive of the
bug, including steps to reproduce the bug, error output logs, etc.

Make sure to designate appropriate tags to your issue.

An issue asking for a new functionality must include an explanation as
to why is such feature necessary.  Note that if you also provide ideas,
literature references, etc. that helps to the implementation of the
requested functionality, there will be more chances of the issue being
solved.

Programming Style
-----------------

Everyone has his/her own programming style, I respect that.  However,
some people have [terrible style](http://www.abstrusegoose.com/432).
Following good coding practices (see
[PEP 8](https://www.python.org/dev/peps/pep-0008/),
[PEP 20](https://www.python.org/dev/peps/pep-0020/), and
[PEP 257](https://www.python.org/dev/peps/pep-0257/)) makes everyone
happier: it will increase the chances of your code being added to the
main repo, and will make me work less.  I strongly recommend the
following programming guidelines:

  - Always keep it simple.
  - Lines are strictly 80 character long, no more.
  - **Never ever! use tabs (for any reason, just don't).**
  - Avoid hard-coding values at all cost.
  - Avoid excessively short variable names (such as ``x`` or ``a``).
  - Avoid excessively long variable names as well (just try to write a
    meaningful name).
  - Indent with 4 spaces.
  - Put whitespace around operators and after commas.
  - Separate blocks of code with 1 empty line.
  - Separate classes and functions with 2 empty lines.
  - Separate methods with 1 empty line.
  - Contraptions require meaningful comments.
  - Prefer commenting an entire block before the code than using
    in-line comments.
  - Always, always write docstrings.
  - Use ``is`` to compare with ``None``, ``True``, and ``False``.
  - Limit try--except clauses to the bare minimum.
  - If you added a new functionality, make sure to also add its repective tests.
  - Make sure that your modifications pass the automated tests (travis).

Good pieces of code that do not follow these principles will
still be gratefully accepted, but with a frowny face.


Pull Requests
-------------

To submit a pull request you will need to first (only once) fork the
repository into your account.  Edit the changes in your
repository.  When making a commit, always include a descriptive message
of what changed.  Then, click on the pull request button.
