#!/usr/bin/groovy

/*
 * Install and run pyfmt
 *
 * code_dirs is a string representing the paths (space delimted) to pass to pyfmt
 */
def call(String code_dirs) {
    sh "pip3 install git+https://github.com/GooeeIOT/pyfmt.git"
    sh "pyfmt --check ${code_dirs}"
    sh "pip3 uninstall pyfmt"
}
