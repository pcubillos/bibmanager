.. _contributing:

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

An issue asking for a new functionality must include the ``wish list``
tag.  These issues must include an explanation as to why is such
feature necessary.  Note that if you also provide ideas, literature
references, etc. that contribute to the implementation of the
requested functionality, there will be more chances of the issue being
solved.

Programming Style
-----------------

Everyone has his/her own programming style, I respect that.  However,
some people have terrible style (see
http://www.abstrusegoose.com/432).  Following good coding practices
make everyone happy, it will increase the chances of your code being
added to the main repository, and it will make me work less.  I strongly
recommend the following programming guidelines:

  - Always keep it simple.
  - **Lines are strictly 80 character long, no more.**
  - **Never ever! use tabs (for any reason, just don't).**
  - Avoid hard-coding values at all cost.
  - One--two character variable names are too short to be meaningful.
  - Indent with 4 spaces.
  - Put whitespace around operators and after commas.
  - Separate lines (within a common block of code) by at most 0 whitespace lines (yes, zero).
  - Separate blocks of code by at most 1 whitespace lines.
  - Separate methods/functions/clasess by at most 2 whitespace lines.
  - Use a header comment (1+ whole line) to describe a code block.
  - Use in-line comments to describe code withing a block.
  - Necessary contraptions require meaningful comments.
  - Always, always make a docstring.
  - Use ``is`` to compare with ``None``, ``True``, and ``False``.
  - Limit try clauses to the bare minimum.

Good pieces of code that do not follow these principles will
still be gratefully accepted, but with a frowny face.


Pull Requests
-------------

To submit a pull request you will need to first (only once) fork the
repository into your account.  Edit the changes in your
own repository.  When making a commit, always include a descriptive message
of what changed.  Then, click on the pull request button.
