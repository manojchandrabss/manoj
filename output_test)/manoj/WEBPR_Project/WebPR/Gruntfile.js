module.exports = function(grunt) {
  // load all grunt-* tasks automatically
  // so you don't need to provision them manually inside
  // gruntfile
  require('time-grunt')(grunt);
  //require('load-grunt-tasks')(grunt);
  require('jit-grunt')(grunt);

  // setup configuration
  grunt.initConfig({

    // global variables to avoid hardcoding paths in Grunt
    // tasks and commands
    globalConfig: {
      assets: {
        // our custom JS code
        js: ['assets/js/**/*.js'],
        // our custom CSS code
        css: ['assets/css/**/*.css'],
        // client's SASS code
        sass: ['assets/scss/**/*.scss'],
        // our custom HTML code
        html: ['templates/**/*.html'],
        // our handlerbars templates
        hbs: ['templates/handlebars/**/*.handlebars'],
        // where to put assembled (concatentated) files, as well as
        // their minimized versions
        dist: 'assets'
      }
    },
    // task to generate html pages from markdown files
    // we will use it as internal 'changelog/forum' implementation
    // where we share specific details about the implementation
    // (developers to developers)
    pages: {
      posts: {
        // where our markdown files are located
        src: 'docs/dev/posts',
        // where to put html files created from markdown files
        dest: '.dev',
        // template layout for each post
        layout: 'docs/dev/layouts/post.jade',
        // url schema
        url: 'pydoc/:title/'
      }
    },
    // task to check CSS files syntax against
    // best practices
    csslint: {
      // where to take configuration for csslint
      options: {
        csslintrc: '.csslintrc'
      },
      strict: {
        options: {
          import: 2
        },
        // what files to check
        src: []
      }
    },
    // additional js checks to the source code we create that
    // are not available in jshint
    jscs: {
      options: {
        // where to take configuration for csslint
        config: '.jscsrc',
        // if you need output with rule names
        // http://jscs.info/overview.html#verbose
        verbose: true,
        // autofix code style violations when possible.
        // if you set to true, then git watch will run
        // in multiple cycles on change.
        fix: false,
        preset: 'google',
        requireCurlyBraces: ['if']
      },
      // what files to check
      src: [
        '<%= globalConfig.assets.js %>',
        '!assets/js/vendor/*.js'
      ]
    },
    eslint: {
      options: {
        configFile: '.eslintrc.js'
      },
      target: ['<%= globalConfig.assets.js %>',
               '<%= globalConfig.assets.html %>']
    },
    // task to watch changes in real time to specified files and run tasks
    // if we get bower.json updated and install the change immediately
    // also run jshint, jscs checker on changed JS files
    watch: {
      // check if bower is updated and run build task
      bower: {
        // what files to check
        files: ['bower.json'],
        tasks: ['exec:bower_install', 'build']
      },
      // check if JS files got updated and run linters along
      // with js concatenation. Live reload enabled
      scripts: {
        // what files to check
        files: '<%= globalConfig.assets.js %>',
        tasks: ['concat:js', 'jscs', 'eslint'],
        options: {
          livereload: true
        }
      },
      // check if css files got updated and run linters along
      // with css concatentation. Live reload enabled
      css: {
        // what files to check
        files: ['<%= globalConfig.assets.css %>'],
        tasks: ['csslint', 'concat:css'],
        options: {
          livereload: true
        }
      },
      // check if html files got updated and run live reload
      html: {
        // what files to check
        files: '<%= globalConfig.assets.html %>',
        options: {
          livereload: true
        }
      },
      hbs: {
        // what files to check
        files: '<%= globalConfig.assets.hbs %>',
        tasks: ['shell:handlebars'],
        options: {
          livereload: true
        }
      }
    },
    // custom command available inside watch config above
    exec: {
      bower_install: {
        cmd: 'bower install'
      }
    },
    // task to concantenate all JS and CSS of all installed Bower components
    // and generate unminified bower.js and bower.css files
    bower_concat: {
      all: {
        // where to put assembled files
        dest: {
          'js': '<%= globalConfig.assets.dist %>/bower.js',
          'css': '<%= globalConfig.assets.dist %>/bower.css'
        },
        // define dependencies here, so the concatenation happens
        // in correct order
        dependencies: {
          'underscore': 'jquery',
          'alertify.js': 'jquery',
          'bootstrap': 'jquery',
          'jquery.validate.js': 'jquery',
          'jquerypp': 'jquery',
          'bootstrap-table': ['jquery', 'bootstrap']
        },
        // in some cases bower_concat gets bower packages that do
        // not properly define their distr folders/files
        // we can fix it by doing it here
        mainFiles: {
          'bootstrap': [
            'dist/css/bootstrap.css',
            'dist/js/bootstrap.js'
          ],
          'alertify.js': [
            'dist/js/alertify.js',
            'dist/css/alertify.css'
          ],
          'jquerypp': [
            'dist/global/jquerypp.js'
          ]
        }
      }
    },
    // task concatenate our own css and js files
    // so we can use app.js and app.css in debug mode
    concat: {
      js: {
        src: [
          '<%= globalConfig.assets.js %>',
          // excluding before refactoring
          '!<%= globalConfig.assets.dist %>/js/iso/*.js',
          '!<%= globalConfig.assets.dist %>/js/merchant/*.js'
        ],
        dest: '<%= globalConfig.assets.dist %>/app.js'
      },
      css: {
        src: '<%= globalConfig.assets.css %>',
        dest: '<%= globalConfig.assets.dist %>/app.css'
      }
    },
    // task minimize bower.js and produce bower.min.js file
    // as well ass app.min.js from our custom JS files
    uglify: {
      // bower.min.js minification
      bower: {
        options: {
          mangle: true,
          compress: true
        },
        files: {
          '<%= globalConfig.assets.dist %>/bower.min.js': [
            '<%= globalConfig.assets.dist %>/bower.js'
          ]
        }
      },
      // app.min.js minification
      app: {
        options: {
          mangle: true,
          compress: true,
          sourceMap: true
        },
        files: {
          '<%= globalConfig.assets.dist %>/app.min.js': [
            '<%= globalConfig.assets.dist %>/app.js'
          ]
        }
      }
    },
    // task to minimize bower.css and produce bower.min.css file
    // as well ass app.min.css from our custom CSS files
    cssmin: {
      options: {
        shorthandCompacting: false,
        roundingPrecision: -1
      },
      // bower.min.css minification
      bower: {
        files: {
          '<%= globalConfig.assets.dist %>/bower.min.css': [
            '<%= globalConfig.assets.dist %>/bower.css'
          ]
        }
      },
      // app.min.css minification
      app: {
        files: {
          '<%= globalConfig.assets.dist %>/app.min.css': [
            '<%= globalConfig.assets.css %>'
          ]
        }
      }
    },
    jsbeautifier: {
      files: ['<%= globalConfig.assets.js %>',
        '<%= globalConfig.assets.html %>'
      ],
      options: {
        config: '.jsbeautifyrc'
      }
    },
    // https://github.com/nDmitry/grunt-postcss
    // http://goo.gl/1ypUlX
    // allows to run post-processing tasks after our custom
    // css files got concatenated
    postcss: {
      options: {
        map: true,
        processors: [
          // cssnext is obsolete
          // require('postcss-import')(),
          // require('postcss-url')(),
          // require('postcss-cssnext')(),
          // require('postcss-browser-reporter')(),
          // require('postcss-reporter')(),
          require('autoprefixer')({
            browsers: ['last 2 version', 'ie 10', 'ie 11']
          }),
          require('cssnext')(),
          require('precss')()
        ]
      },
      dist: {
        src: '<%= globalConfig.assets.dist %>/app.css',
        dest: '<%= globalConfig.assets.dist %>/app.css'
      }
    },
    // send notifications when task complete
    notify: {
      build: {
        options: {
          message: 'Build is completed successfully!'
        }
      }
    },
    // this should be used as isolated command
    // it will compile app.min.css, app.min.js
    // bower.min.css, bower.min.js under new revisions
    // insisde assets/revs folder which could be useful for
    // deplpyment in CDN scenario when files are cached by CDN
    // https://www.npmjs.com/package/grunt-filerev
    // we can also use this for images and other binary files
    filerev: {
      options: {
        algorithm: 'md5',
        length: 8
      },
      appfiles: {
        src: ['assets/*.min.css', 'assets/*.min.js'],
        dest: 'assets/revisions'
      }
    },
    // generate javascript documentation
    jsdoc: {
      dist: {
        src: ['assets/js/**/*.js', 'templates/users/*.html', 'README.md'],
        options: {
          destination: '.dev/jsdoc',
          template: 'node_modules/ink-docstrap/template',
          configure: '.jsdoc.conf.json'
        }
      }
    },
    // apidoc generation
    apidoc: {
      apps: {
        src: 'apps/',
        dest: '.dev/apidoc/'
      }
    }, // these are additional shell commands available inside grunt tasks
    shell: {
      // shell command to install bower package
      bowerinstall: {
        command: function(libname) {
          return 'bower install ' + libname + ' -S';
        }
      },
      // shell command to uninstall bower package
      boweruninstall: {
        command: function(libname) {
          return 'bower uninstall ' + libname + ' -S';
        }
      },
      // shell command to update bower package
      bowerupdate: {
        command: function(libname) {
          return 'bower update ' + libname;
        }
      },
      // command to copy git hooks from repo inside your own
      // .git folder
      hooks: {
        command: 'cp .git-hooks/pre-commit .git/hooks/'
      },
      // shell command to minify and pre-compile handlebars templates
      handlebars: {
        command: 'handlebars templates/handlebars ' +
          ' -m -f assets/handlebars/templates.js'
      },
      // generate tags
      ctags: {
        command: 'ctags -e -R apps/ libs/ assets/js/* templates TAGS'
      },
      // perform pep8 check
      pep8: {
        command: 'flake8 --config=.flake8 apps'
      },
      // generate tags
      autopep8: {
        command: 'autopep8 --recursive --in-place --aggressive  apps'
      }
    },
    // clean any pre-commit hooks in .git/hooks directory
    clean: {
      hooks: ['.git/hooks/pre-commit']
    }
  });

  // default task to run when you run grunt from CLI
  // it will run linters against JS code
  grunt.registerTask('default', ['jscs', 'eslint', 'csslint', 'shell:pep8']);
  grunt.registerTask('pep8', ['shell:pep8']);
  grunt.registerTask('autopep8', ['shell:autopep8']);

  // aggregated build bower assets into single file
  // and then minify it
  grunt.registerTask('build', [
    'bower_concat',
    'concat',
    'postcss',
    'uglify',
    'cssmin',
    // 'gendocs',
    'shell:ctags',
    'shell:handlebars',
    'notify:build'
  ]);

  // if you want to install any bower dep and quickly rebuild the bower.css/js
  // and produce their min versions simply type grunt bowerinstall <libname>
  // like grunt bowerinstall stringjs you will get this output:
  // https://goo.gl/HfkhP1
  grunt.registerTask('bowerinstall', function(library) {
    grunt.
    task.
    run('shell:bowerinstall:' + library);

    grunt.
    task.
    run('build');
  });
  // same purpose as above but to uninstall the package
  grunt.registerTask('boweruninstall', function(library) {
    grunt.
    task.
    run('shell:boweruninstall:' + library);

    grunt.
    task.
    run('build');
  });
  // same purpose as above but to update the package
  grunt.registerTask('bowerupdate', function(library) {
    grunt.
    task.
    run('shell:bowerupdate:' + library);

    grunt.
    task.
    run('build');
  });

  // generate docs
  grunt.registerTask('gendocs', function() {
    // grunt.task.run('pages');

    grunt.
    task.
    run('jsdoc');

    // grunt.
    // task.
    // run('apidoc');
  });

  // clean the .git/hooks/pre-commit file then copy in the latest version
  grunt.registerTask('hookmeup', [
    'clean:hooks',
    'shell:hooks'
  ]);
};
