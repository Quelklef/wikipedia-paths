# wikipedia-paths
A fun li'l script which finds the shortest path between two pages on Wikipedia.

Most applications which do this work (I assume) by way of a database. This is great for speed; however, it means that the data kept loaclly on the server is not encessarily up-to-date with Wikipedia.

This is the key difference in my script: My script uses no database but contacts Wikipedia directly, guaranteeing (unless the wiki page changes from script start to script end) that the result is the correct answer. However, this makes it extremely slow (e.g. finding its way from Jigsaw Puzzle to Insanity, a fourth degree link (Jigsaw Puzzle => Moon => Full Moon => Insanity) on a ~10-15mbps internet took 1h 23m based on Python's `time.time()` and 11m 52s based on `time.clock()`)

Written in Python 2.7.12
