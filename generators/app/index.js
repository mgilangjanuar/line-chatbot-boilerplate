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
        type    : 'input',
        name    : 'interpreter.python',
        message : 'Command for python?',
        default : 'python3'
      },
      {
        type    : 'input',
        name    : 'interpreter.pip',
        message : 'Command for pip?',
        default : 'pip3'
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
      {
        type    : 'input',
        name    : 'redis.host',
        message : 'Redis host?',
        default : 'localhost'
      },
      {
        type    : 'input',
        name    : 'redis.port',
        message : 'Redis port?',
        default : 6379
      },
      {
        type    : 'input',
        name    : 'route',
        message : 'Chatbot callback route?',
        default : '/callback'
      },
      {
        type    : 'confirm',
        name    : 'db.useDb',
        message : 'Would you like use database?',
        default : true
      },
      {
        when    : (resp) => {
          return resp.db.useDb
        },
        type    : 'input',
        name    : 'db.collection',
        message : 'MongoDB collection name?'
      },
      {
        when    : (resp) => {
          return resp.db.useDb
        },
        type    : 'input',
        name    : 'db.host',
        message : 'MongoDB host?',
        default : 'localhost'
      },
      {
        when    : (resp) => {
          return resp.db.useDb
        },
        type    : 'input',
        name    : 'db.port',
        message : 'MongoDB port?',
        default : 27017
      },
      {
        when    : (resp) => {
          return resp.db.useDb
        },
        type    : 'input',
        name    : 'db.username',
        message : 'MongoDB username?',
        default : null
      },
      {
        when    : (resp) => {
          return resp.db.useDb
        },
        type    : 'input',
        name    : 'db.password',
        message : 'MongoDB password?',
        default : null
      },
    ])
    .then((answers) => {
      this.projectName = answers.name.replace(/ /g, "-")
      this._cloning((err, stdout, stderr) => {
        if (!err) {
          this._setup_env(answers.envs)
          this._setup_git(answers.git, (err, stdout, stderr) => {
            if (!err) {
              this._setup_index(answers.redis, answers.db, answers.route, (err, stdout, stderr) => {
                if (!err) {
                  this._setup_python(answers.interpreter, (err, stdout, stderr) => {
                    if (!err) {
                      this.log.info(`Your project has served in ${this.projectName} directory`)
                      this.log.info(`Run cd ${this.projectName}; source env/bin/activate;`)
                      this.log.info('Happy coding! :)')
                    } else {
                      this.log.error(err)
                    }
                  })
                } else {
                  this.log.error(err)
                }
              })
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

  _cloning(callback) {
    this.log.create(`${this.projectName} project`)
    return exec(`git clone https://github.com/mgilangjanuar/line-chatbot-boilerplate.git ${this.projectName}`, callback)
  }

  _setup_env(envs) {
    return this.fs.copyTpl(
      this.templatePath(envs.useWitToken ? '.env.with_wit.tpl' : '.env.without_wit.tpl'),
      this.destinationPath(`${this.projectName}/.env`), envs
    )
  }

  _setup_git(git, callback) {
    this.log.create(`${this.projectName}/.git`)
    return exec(`rm -rf ${this.projectName}/.git; git init ${this.projectName}`, (err, stdout, stderr) => {
      if (!err && git.useRepository) {
        exec(`git --git-dir=${this.projectName}/.git remote add origin ${git.repository}`, callback)
      } else {
        callback(err, stdout, stderr)
      }
    })
  }

  _setup_index(redis, db, route, callback) {
    var dbUsername  = db.username ? `\'${db.username}\'` : 'None'
    var dbPassword  = db.password ? `\'${db.password}\'` : 'None'
    return exec(`rm -rf ${this.projectName}/index.py`, (err, stdout, stderr) => {
      if (!err) {
        this.fs.copyTpl(
          this.templatePath('index.tpl.py'),
          this.destinationPath(`${this.projectName}/index.py`), {
            redisConfiguration: `redis.StrictRedis(host=\'${redis.host}\', port=${redis.port}, db=0)`,
            importMongoengine: db.useDb ? 'from mongoengine import connect' : '',
            createMongoConnection: db.useDb ? `connect(\'${db.collection}\', host=\'${db.host}\', port=${db.port}, username=${dbUsername}, password=${dbPassword})` : '',
            routeCallback: route
          }
        )
        this._setup_formatting(callback)
      } else {
        this.log.error(err)
      }
    })
  }

  _setup_formatting(callback) {
    return exec(`sed "s/&#39;/'/g" < ${this.projectName}/index.py > ${this.projectName}/index.new.py`, (err, stdout, stderr) => {
      if (!err) {
        exec(`rm -rf ${this.projectName}/index.py; mv ${this.projectName}/index.new.py ${this.projectName}/index.py`, callback)
      }
    })
  }

  _setup_python(interpreter, callback) {
    this.log.create('a coffee')
    return exec(`${interpreter.python} -m venv ${this.projectName}/env; ./${this.projectName}/env/bin/${interpreter.pip} install -r ${this.projectName}/requirements.txt`, callback)
  }
}