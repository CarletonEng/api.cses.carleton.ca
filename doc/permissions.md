# Permissions

The API uses a flexible permission system to control access levels.  Each user has a set of permissions and each authorization token a user has can access a subset of them.  This allows creation of restricted authorization tokens to limit access.

## Recognized Permissions

### wheel

The wheel permission puts you in the drivers seat.  You can change anyones permissions and reset anyones password.  Anyone with the wheel permission can gain complete access to the system by giving themselves permissions or hijacking another user's account.

### personw

The personwrite permission allows you to modify any user.  This includes names, emails, passwords and other information.  The only exception to this is that you can't change the password or recovery information of a user with the wheel permission unless you have the wheel permission as well.

### personr

Allows reading "private" information such as email, phone and student number of any user.

### postw

Allows creating and editing posts, including pages and articles.

It should be noted that at this time posts are allowed to contain any HTML and therefore could have scripts embedded in them.  This means that some with the `postw` could escalate their privileges by stealing other user's sessions.  Only give this permission to people you trust.

### selfw

Allow changing of your own information such as password, email, name and others.

### selfr

Allow reading of your own "private" information.

### tbt

Allow managing of the text book trade system include adding, selling and removing books.

### upload

Allow uploading files to the server.
