# Example

to start using bender you must define a [resource type](https://concourse.ci/configuring-resource-types.html)

```yaml
# Defined custom resource
resource_types    :
  - name: bender-resource
    type: docker-image
    source:
      repository: quay.io/ahelal/bender
      tag: latest
```

## `Example 1`: A simple trigger when `@bender` is mentioned in `planet_express` channel

``` yaml
resources         :
  - name          : bender
    type          : bender-resource
    source        :
      slack_token : ((token))
      channel     : "planet_express"
jobs       :
  - name   : Simple trigger
    plan   :
      - get: bender
        version: every
        trigger: true

      - task : This job will be triggered
        file: something/task.yml
```

## `Example 2`: A simple trigger when `@bender` is mentioned in `planet_express` channel and reply on status

``` yaml
resources         :
  - name          : bender
    type          : bender-resource
    source        :
      slack_token : ((token))
      channel     : "planet_express"
jobs       :
  - name   : Simple trigger
    plan   :
      - get: bender
        version: every
        trigger: true
      - put: bender
        params:
            path: "bender"
            reply: "Start job."
      - task : This job will be triggered
        file: something/task.yml
        on_success:
            put: bender
            params:
              path: "bender"
              reply: "Done with job."
        on_failure:
            put: bender
            params:
              path: "bender"
              reply: "Sorry job failed."
```

## `Example 3`: Simple deploy with some regex

We want to be able to deploy `@bender superApp deploy`

``` yaml
resources         :
  - name          : bender
    type          : bender-resource
    source        :
      slack_token : ((token))
      channel     : "planet_express"
      # Note we escape \ with \\
      grammar     : "^(superApp)\\s+(deploy)($|\\s+)"
jobs       :
  - name   : Simple deploy
    plan   :
      - get: bender
        version: every
        trigger: true

      - task : Deploy superApp
        file: something/deploy.yml
```

## `Example 4`: Realistic deploy scenario with some regex and subgroups

```yaml
resources         :
  - name          : bender
    type          : bender-resource
    source        :
      slack_token : ((token))
      channel     : "planet_express"
      # Note we escape \ with \\
      grammar     : "^(superApp)\\s+(deploy)\\s+(live|staging)\\s+(\\S+)($|\\s+)"
      # create key=value file
      template    : "ENVIRONMENT={{ regex[2] }}\nVERSION={{ regex[3] }}\n"

jobs       :
  - name   :  Hello
    plan   :
      - get: bender
        version: every
        trigger: true

      - put: bender
        params:
          path: "bender"
          reply: "Starting deployment {{ENV['ATC_EXTERNAL_URL']}}/teams/{{ ENV['BUILD_TEAM_NAME'] }}/pipelines/{{ENV['BUILD_PIPELINE_NAME']}}/jobs/{{ENV['BUILD_JOB_NAME'}}/builds/{{ENV['BUILD_NAME']}}"

      - task              : Deploying something
        config            :
          platform        : linux
          image_resource  :
            type          : docker-image
            source        : {repository: quay.io/hellofresh/ci-ansible}
          inputs          :
           - name         : bender
          run             :
            path          : /bin/sh
            args          :
                            - -exc
                            - |
                              # source our template file
                              . bender/template_file.txt
                              # Deploy with passed in argument
                              deploy_command -i ${ENVIRONMENT} -v ${VERSION}
```

## `Example 5`: Realistic deploy scenario with some regex and named subgroups

Same as Example 4 with the following difference `grammar: "^(?P<app>superApp)\\s+(?P<command>deploy)\\s+(?P<environment>live|staging)\\s+(?P<version>\\S+)($|\\s+)"` and `template: "ENVIRONMENT={{ regex[2] }}\nVERSION={{ regex[3] }}\n"`

## `Example 6`: Bumping versions

```yaml
resources         :
  - name          : semantic-version
    ...
  - name          : bender
    type          : bender-resource
    source        :
      slack_token : ((token))
      channel     : "planet_express"
      # Note we escape \ with \\
      grammar     : "^(superApp)\\s+(release)\\s+(minor)($|\\s+)"

jobs       :
  - name   :  Do minor release
    plan   :
      - get: bender
        version: every
        trigger: true
      - put: semantic-version
        params:
          bump: minor
      - put: bender
        params:
          path: "bender"
          reply: "Release "
```
