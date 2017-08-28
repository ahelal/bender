# bender Resource

A  Concourse resource that can trigger any job (deployments, releases, ...) using slack.
Check [examples](#Examples)

## Source Configuration

* `slack_token`: *Required*. The slack token to be used. For more info check [slack documentation](https://api.slack.com/docs/token-types#bot).

* `channel`: *Required*. The channel name to be used by the bot.

* `bot_name`: *Optional*, *default `bender`*. The bot name will be used to identify and filter messages. All messages must be addressed to the bot, eg.: `@bot_name some message`.

* `grammar`: *Optional.* If not defined bender will respond to all mentions `@bot_name` and If grammar is defined bender will **only** respond to messages matching the regex expression. Use [python regular expression](https://docs.python.org/2/library/re.html) syntax. See [examples](#Examples) for inspiration.

* `template`: *Optional*. A string that will be evaluated and written to `template_filename` can be used as an input file for further jobs in the pipeline.

* `template_filename`: *Optional*, *default `template_file.txt`*. The file name for a generated template.

## Behavior

### `check`: Check for new messages that match the rules

Check will report a new version;`timestamp`; if message is addressed to `@bot_name` in the selected `channel` **and** if `grammar` is defined, it *must* match the regular expression defined in `grammar`.

#### `check Parameters`

Check accepts no params.

### `in`: Get the message

A file **bender.json** will be created with the message payload.

if `template` is defined it will be evaluated and written to `template_filename`. For more info on template syntax read [Template section](#Template). For example on usage, check the [examples](#Examples) section.

#### `in Parameters`

In accepts no params.

### `out`: Reply to original message

Replies to the original message in a thread format.

#### `out Parameters`

* `path`: *Required.* The path of the resource name.

* `reply`: *Required.* The message to be used as reply. Supports [template format](#Template).

### Template

The template uses python [Jinja2](http://jinja.pocoo.org/docs/2.9/) engine.

* `variables`: You can access variables using curly braces `{{ VARIABLE_NAME }}`.
   All environmental variables are accessible through `{{ ENV['PATH'] }}`.
   Concourse exposes some metadata info like job_name, build, for more info [check concourse website](https://concourse.ci/implementing-resources.html#resource-metadata).
   The regex groups are accessible to the template engine as `{{ regex }}` if you used *subgroups* in your expression you can access each group with index `{{ regex[0] }}`. If you used *named subgroups* you can access them as dictionary `{{ regex['name'] }}`.

* `white spaces`: You can use `\n` for new lines `\t` for tabs in your template.

* `filters`: You can use Jinja2 [builtin filters](http://jinja.pocoo.org/docs/2.9/templates/#builtin-filters).

## Tips

* Test your regex using something like [regexr.com](http://regexr.com/), it is better to use [named subgroups](http://www.regular-expressions.info/brackets.html).

* Note that you need to escape the backslash with another backslash in yaml,  eg.: `\s+` should be `\\s+`

* Use `\s+` between commands to give a little bit of room for user send an extra space in the message.

* You probably want to define **version: every** and in your **trigger: true** so the resource will go through all the messages and trigger the jobs.

```yaml
      - get: bender
        version: every
        trigger: true
```

* If you have multiple triggers on the same channel it is better to use a different bot token for each. check TODO

## Examples

Check [examples.md](examples.md)

## TODO

* At the moment Bender depend on `timestamp` and slack to mark last as message read. Usually concourse should handle this natively with *check* version. Using **slack unread message** will improve speed, but downside you can't have multiple triggers per channel with same token. This only affects the check method. So need to support native concourse resource checks too.

* Increase code coverage

## Contribution

* [aleerizw](https://github.com/aleerizw)
* [rnurgaliyev](https://github.com/rnurgaliyev)
