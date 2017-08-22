# qtbot
### A Discord bot I wrote to learn some Python.
### Mostly modular & inspired by Danny whose project can be found [here](https://github.com/Rapptz/RoboDanny)
### Uses *a lot* of APIs.
#### More specifically:
* Wordnik: `.define`
* Wolfram Alpha: `.calc`
* WeatherUnderground: `.w` and `.fc`
* TMDb: `.movie`
* Riot Games: `.ucf` (updateChampFile)
* Champion.gg: `.champ`
* NewsApi.org: `.news`
* WhatIsMyMMR.com: `.elo`
---
* Admin:
  * `load`   Loads an extension.
  * `unload` Unloads an extension.
  * `reload` Reloads an extension.
* AskAsk:
  * `g`      Get search results from an *alternative source* now that Google has blocked me.
* Calculator:
  * `calc`   Calculate like, anything (wolfram alpha).
* Comics:
  * `xkcd`   Search for a vaguely relevant xkcd comic (if you're lucky). Otherwise returns a random comic.
* Dictionary:
  * `define` Provides the definition of *a* word.
  * `ud`     Consult the world's leading dictionary.
* Generic:  
  * `akick`  Don't use this.
  * `ball`   Ask the magic 8ball.
  * `love`   Give someone, or something, some lovin'.
  * `resame`
  * `same`   
  * `slap`   Teach someone a lesson.
  * `todo`   A to-do list for myself.
  * `unsame`
* Giphy:
  * `gif`    Returns a random gif matching a query.
  * `thanks` Thank your overlord, qtbot.
* League:
  * `elo`    Get League of Legends elo.
  * `mmr`    Alias for the above.
  * `ci`     Get LoL champion information from Champion.gg.
  * `ucf`    Update champion file (Owner Only).
* TMDb:
  * `movie`  Get movie information.
  * `show`   Get TV show information.
* News:
  * `news`   Get the top (1 - 5) news articles from Google News.
* OSRS:
  * `ge`     Get the buying/selling price and quantity of an OSRS item.
* Weather:
  * `az`     Add zipcode to userfile.
  * `fc`     Wunderground weather forecast for `zip`.
  * `wt`     Wunderground current weather for `zip`.
* Wiki:
  * `wiki`   Search for a loosely related wikipedia article.
* YouTube:
  * `yt`     Returns some matching youtube videos for a query.
* No Category:
  * `help`   Shows this message.
  * `uptime` Get current uptime.
