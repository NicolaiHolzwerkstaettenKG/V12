# Introduction Letter

Dear developer,

in future you may need to modify or extend this modules which is why I want to leave you some notes.

## Respect the DATEV rules
Note that this module is strictly developed by the official DATEV documentation and should not be altered against it.
https://developer.datev.de/portal/dxso

DO NOT MODIFY STUFF INSIDE THE "datev" DIRECTORY UNLESS YOU REALLY KNOW WHAT YOU'RE DOING!
The structure, docs and validations are dictated by DATEV.
Don't touch it unless DATEV released new API version. If so, again, go strictly by their docs!

## Respect Odoo Standard
This module is designed to work with odoo standard.
If required you may extend it with required fields but do not alter any code logic.

## Respect general coding rules
- No CopyPasta
- Method overriding and overloading: okay, overwriting: nay!
- Respect others work, call your super ;)

## No customer specific changes
You are completely wrong here! They are a pain to maintain/migrate and sooner or later will f.. up yourself and most likely your other customers. Please move such changes to an own, totally separated, module.

## Work in english!
There are translation files for a good reason.

## Documentation
Finally the code is well commented, so read the comments and comment your changes.
We work by the Google Python Style Guide.
https://google.github.io/styleguide/pyguide.html

Happy coding!
/ Jan Brodersen
