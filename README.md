# pwdgen - password generator

The project of a simple console password generator.

## Usage
The utility allows you to generate passwords (passphrases) using command line parameters or through a simple console menu.

You can always check available options by running
```bash
main.py --help
```

Here are some basic examples to get you started

```bash
# generate password with predefined complexity levels
main.py [--compl {weak,standard,strong}] [-c COUNT]
# for example: generate 6 strong password
main.py -compl strong -c 6

# generate password with user (custom) parameters
main.py [-c COUNT] [-w WORD_COUNT] [-l LETTER_COUNT] [-n] [-s] [-u]
# for example: generate 2 password consisting of 4 words and numbers
main.py -c 2 -w 4 -n

# generate password using xkcd library
main.py [--xkcd {weak,standard,strong,super}] [-c COUNT]
# for example: generate 3 xkcd super password
main.py -xkcd super -c 3
```

You can also use the simplest console menu, which can be called with the command

```bash
main.py --main-menu
```

## Basic application features
In this application, you can generate a password based on Russian dictionary words with delimiters and/or prefixes. There are 4 levels of complexity of created passwords:
1. weak
2. standard
3. strong
4. custom

_Weak_, _standard_ and _strong_ passwords are generated based on the specified parameters. _Custom_ (user) password settings can be set manually.

### Custom passwords
To generate _custom_ passwords, you can use both command line options and the utility menu. For example, 
```bash
main.py -c 2 -w 3 -l 2 -n -s -u
# or
main.py --count 2 --word-count 3 --char-count 2 --num --special-chars --upper-case
```
In this case, all valid options have been used. As a result, we get 2 passwords (`-c 2`), consisting of:
- two first letters (`-l 2`) of three vocabulary words (`-w 3`) of the Russian language
- every first letter of a word is capitalized (`-u`)
- numbers are used (`-n`)
- special characters are used (`-s`)


To do this, you can use menu (item 6) or you can edit the configuration file [conf.ini](conf.ini).

When editing [conf.ini](conf.ini), it is only allowed to change the parameter values:
- words_count - an integer in the range 2..6
- char_count - an integer in the range 3..5
- use_numbers - True/False
- use_special - True/False
- use_upper_case - True/False

Deleting or changing a parameter, entering a parameter value outside of the allowed values, will result in the use of the default parameters.

## Requirements (Installation)
You need the [following](requirements.txt) libraries to use the project.
