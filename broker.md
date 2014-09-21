MEI/LilyPond Broker
==============================

This file collects ideas for the "broker" application mentioned [here](https://lists.uni-paderborn.de/pipermail/mei-l/2014/001308.html).

The idea is basically to automate conversion between MEI and LilyPond, ensuring consistency and correctness.

NOTE however that there's no reason to think about this program in too much detail until both mei2ly and ly2mei are reasonably functional. Otherwise there's nothing to broke!

I think we'd be better off building an extension for Mercurial than buildling a new set of scripts or a new application that wraps Git. Although Git is more popular, it is extremely complicated, and not alway easy to learn. If we choose to build on Git, we'll have to either completely replace the user-facing components or ask people to use a combination of Git and our scripts, which further complicates an already-complicated workflow. If we build on Mercurial, on the other hand, we can *both* modify built-in Mercurial commands *and* add our own commands. This way, people already accustomed to Mercurial can use the software as they expect, while new users will be asked to learn a single additional program, and it'll be one that they can take with them to their other work.

The reasons for such bold assertions are numerous, and should be more fully explained before we start building something. I also have to explain why Git and Mercurial are the only two options I considered. I also have to explain exactly what sort of functionality I'm imagining in this program, and why I feel the best choice is to build on existing version control software rather than to start from scratch.
