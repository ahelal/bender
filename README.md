# Bender concourse resource

[![Build Status](https://travis-ci.org/ahelal/bender.svg?branch=master)](https://travis-ci.org/ahelal/bender) [![Docker Repository on Quay](https://quay.io/repository/ahelal/bender/status "Docker Repository on Quay")](https://quay.io/repository/ahelal/bender)

A  Concourse resource that can trigger any job (deployments, releases, ...) using slack.

Check [examples](examples.md) page for usage.

*NOTE: Bender is still young, Your input and contribution is highly appreciated.*

## Deploying to Concourse

You can use the docker image by defining the  [resource type](https://concourse.ci/configuring-resource-types.html) in your pipeline YAML.

```yaml
resource_types    :
  - name: bender-resource
    type: docker-image
    source:
      repository: quay.io/ahelal/bender
      tag: latest
```

## Source Configuration

* `slack_token`: *Required*. The slack token to be used. For more info check [slack documentation](https://api.slack.com/docs/token-types#bot).

* `channel`: *Required*. The channel name to be used by the bot.

* `bot_name`: *Optional*, *default `bender`*. The bot name will be used to identify and filter messages. All messages must be addressed to the bot, eg.: `@bot_name some message`.

* `as_user`: *Optional.*, *default `true`*. By default use the authed user, if `false` you can customize the `bot_name`, `bot_icon_emoji` and `bot_icon_ur`.

* `bot_icon_emoji`: *Optional.* Emoji to use as the icon for this message. Overrides `bot_icon_url`. Must be used in conjunction with `as_user` set to false, otherwise ignored.

* `bot_icon_url`: *Optional.* URL to an image to use as the icon for this message. Must be used in conjunction with `as_user` set to false, otherwise ignored.

* `mention`: *Optional.* Only respond to mention `@bot_name` this will only work with `as_user: false`, otherwise ignored.

* `grammar`: *Optional.* If not defined bender will respond to all mentions `@bot_name` and If grammar is defined bender will **only** respond to messages matching the regex expression. Use [python regular expression](https://docs.python.org/2/library/re.html) syntax. See [examples](examples.md) page for inspiration.

* `template`: *Optional*. A **string** that will be evaluated and written to `template_filename` can be used as an input file for further jobs in the pipeline.

* `template_filename`: *Optional*, *default `template_file.txt`*. The file name for a generated template.

* `slack_unread`: *Optional*, *default `false`*. If set to true, The state of **slack unread message** will be used instead of of the last version reported by concourse. This will improve speed, but downside you can't have multiple triggers per channel with same token and it's non-standard concourse behavior. This only affects the check method.

## Behavior

### `check`: Check for new messages that match the rules

Check will report a new version;`timestamp`; if message fits **all** the criteria.

* If `mention` is *true* the message must be addressed to `@bot_name` in the selected `channel`.

* If `grammar` is defined, it *must* match the regular expression defined in `grammar`.

#### `check Parameters`

Check accepts no params.

### `in`: Get the message

A file **bender.json** will be created with the message payload.

if `template` is defined it will be evaluated and written to `template_filename`. For more info on template syntax read [template section](#template). For example on usage, check the [examples](examples.md) page.

#### `in Parameters`

In accepts no params.

### `out`: Reply to original message

Replies with a message to the selected `channel`.

#### `out Parameters`

* `reply`: *Required/optional*. A **string** or **file path** to be used as reply. Supports [template format](#template). *Must be defined if `reply_attachments` is not defined.*

* `reply_attachments`: *Required/optional*. A **string** or **JSON file path** to be used as reply in [slack attachment format](https://api.slack.com/docs/message-attachments). You can use [messages builder](https://api.slack.com/docs/messages/builder) Supports [template format](#template). *Must be defined if `reply` is not defined.*

* `reply_thread`: *optional*, *default `False`*. If enabled will post reply to original message as a thread.

* `path`: *required*. The path of the resource name. This is used to get context from original message.

### Template

The template uses python [Jinja2](http://jinja.pocoo.org/docs/2.9/) engine.

* `variables`: You can access variables using curly braces `{{ VARIABLE_NAME }}`.
   All environmental variables are accessible through `{{ ENV['PATH'] }}`.
   Concourse exposes some metadata info like job_name, build, for more info [check concourse website](https://concourse.ci/implementing-resources.html#resource-metadata).
   The regex groups are accessible to the template engine as `{{ regex }}` if you used *subgroups* in your expression you can access each group with index `{{ regex[0] }}`. If you used *named subgroups* you can access them as dictionary `{{ regex['name'] }}`.
   The original user who initiated the trigger is accessible as variable `{{ user }}`. You can also add `@{{ user }}` to mention the user.

* `white spaces`: You can use `\n` for new lines `\t` for tabs in your template.

* `filters`: You can use Jinja2 [builtin filters](http://jinja.pocoo.org/docs/2.9/templates/#builtin-filters).

## Tips

* Test your regex using something like [regexr.com](http://regexr.com/), it is better to use [named subgroups](http://www.regular-expressions.info/brackets.html).

* Note that you need to escape the backslash with another backslash in yaml,  eg.: `\s+` should be `\\s+`

* Use `\s+` between commands to give a little bit of room for user send an extra space in the message.

* You probably want to define **version: every** and **trigger: true** so the resource will go through all the messages and trigger the jobs.

```yaml
      - get: bender
        version: every
        trigger: true
```

* By default concourse resource are checked every 1m. If you want to setup multi resources you will exhaust your Slack API limits fast. You can configure slack to do an API call to your concourse using [slack outgoing webhooks](https://api.slack.com/custom-integrations/outgoing-webhooks), [concourse webhook_token](https://concourse.ci/single-page.html#webhook_token) and increase [check_every](https://concourse.ci/single-page.html#check_every) to higher eg. 1h. You can also use different [Slash commands](https://api.slack.com/slash-commands) instead of web hooks.

## TODO

* Increase code coverage
* Restrict per user_group
* lock example

## Contribution

* [aleerizw](https://github.com/aleerizw)
* [rnurgaliyev](https://github.com/rnurgaliyev)
