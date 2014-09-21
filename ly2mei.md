ly2mei
======================

This document collects ideas for the "LilyPond to MEI" program, tentatively called ly2mei.

The program will probably accept only a subset of LilyPond's full functionality. We can and should define this clearly with a "whitelist."

The program should accept incomplete LilyPond documents, so that people may convert fragments of LilyPond to fragments of MEI, as in: `a4` becomes `<note pname="a" dur="4"/>`.

In terms of which programming language to choose, I'm quite conflicted. It seems like Python would be a good and natural choice, and it's becoming increasingly well-known and widely used. (Plus I know it already). However, I'd really like to learn another language, and embarking on a project like this provides a good opportunity for that. I would be especially interested in learning Haskell or Mozilla's new Rust, but I'm concerned what would happen to the program if I/we choose one of those less popular languages. Would it further discourage potential contributors, considering we're already drawing from a relatively small base of possible contributors? So I'm going to start writing the program in Python, even though it will be less fancy and less efficient (than Haskell or Rust), and when it comes time to do a re-write, we can reconsider this issue.

We'll have to face the issue of what to do with LilyPond things that don't have an MEI equivalent. Maybe we'll make an extension to MEI to hold this data.

I also wonder if it would be profitable to start with LilyPond's "all-Scheme" score, rather than the LilyPond-language document. It'll be more explicit, and *possibly* less error-prone, but then we'll have to write a Scheme interpreter. But then... at least we have a clearer specification in mind? And maybe that would also make ly2mei more resilient to small changes in LilyPond's syntax. But it'll also make it more difficult for us to specify exactly what we can convert.
