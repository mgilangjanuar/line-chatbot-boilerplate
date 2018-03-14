var Generator = require('yeoman-generator')
var exec      = require('child_process').exec

module.exports = class extends Generator {

  constructor(args, opts) {
    super(args, opts)
    this.option('babel')
  }

  prompting() {
    return this.prompt([
      {
        type    : 'input',
        name    : 'name',
        message : 'Your project name?'
      },
      {
        type    : 'input',
        name    : 'envs.channelSecret',
        message : 'LINE Messaging channel secret?'
      },
      {
        type    : 'input',
        name    : 'envs.channelAccessToken',
        message : 'LINE Messaging channel access token?'
      },
      {
        type    : 'confirm',
        name    : 'envs.useWitToken',
        message : 'Would you like to use Wit.ai?',
        default : true
      },
      {
        when    : (resp) => {
          return resp.envs.useWitToken
        },
        type    : 'input',
        name    : 'envs.witToken',
        message : 'Wit app token?'
      },
      {
        type    : 'confirm',
        name    : 'git.useRepository',
        message : 'Would you like to add remote repository?',
        default : true
      },
      {
        when    : (resp) => {
          return resp.git.useRepository
        },
        type    : 'input',
        name    : 'git.repository',
        message : 'Repository URL?'
      },
    ])
    .then((answers) => {
      this._cloning(answers.name, (err, stdout, stderr) => {
        if (!err) {
          this._setup_env(answers.name, answers.envs)
          this._setup_git(answers.name, answers.git, (err, stdout, stderr) => {
            if (!err) {
              this.log.info('happy coding! :)')
            } else {
              this.log.error(err)
            }
          })
        } else {
          this.log.error(err)
        }
      })
    })
  }

  _cloning(projectName, callback) {
    projectName = projectName.replace(/ /g, "-")
    this.log.create(`${projectName} chatbot project`)
    return exec(`git clone https://github.com/mgilangjanuar/line-chatbot-boilerplate.git ${projectName}`, callback)
  }

  _setup_env(projectName, envs) {
    projectName = projectName.replace(/ /g, "-")
    return this.fs.copyTpl(
      this.templatePath(envs.useWitToken ? '.env.with_wit.tpl' : '.env.without_wit.tpl'),
      this.destinationPath(`${projectName}/.env`), envs
    )
  }

  _setup_git(projectName, git, callback) {
    projectName = projectName.replace(/ /g, "-")
    this.log.create('initiate git')
    return exec(`rm -rf ${projectName}/.git; git init ${projectName}`, (err, stdout, stderr) => {
      if (!err && git.useRepository) {
        exec(`git --git-dir=${projectName}/.git remote add origin ${git.repository}`, callback)
      } else {
        callback(err, stdout, stderr)
      }
    })
  }

}
