# iceshelf [![Build Status](https://travis-ci.org/mrworf/iceshelf.svg?branch=master)](https://travis-ci.org/mrworf/iceshelf)

A simple tool to allow storage of private, incremental backups using Amazon's Glacier storage. It uses par2, tar, bzip2, gpg, json and nice stuff like that to accomplish the job.

# Features

- Encrypts all backups using GPG private/public key
- Signs all files it uploads (tamper detection)
- Can upload separate PAR2 file for parity correction (allows for a certain amount of bitrot)
- Supports segmentation of upload (but not of files, yet)
- Primarily designed for AWS Glacier but can be used with other services
- Tracks backups locally to help locate the file needed to restore
- Keeps the exact directory structure of the backed up files
- Most features can be turned on/off and customized
- Provides paper-based GPG key backup/restore solution

Due to the need to work well with Glacier, any change to a file will cause it
to reupload the same file (with the new content). This backup solution is not
meant to be used on files which change often.

It's an archiving solution for long-term storage which is what Glacier excels
at. Also the reason it's called iceshelf. To quote from wikipedia:

> An ice shelf is a thick floating platform of ice that forms where a glacier or ice sheet flows down to a coastline and onto the ocean surface

*and yes, this would probably mean that time runs in reverse, but bear with
me, finding cool names (phun intended) for projects is not always easy*

# How does it all work?

1. Loads backup database if available
2. Empties prep directory of any files
3. Creates a tar file (recreating directory structure) until no more are found or limit is hit. If this wasn't the first run, only new or changed files are added
4. Depending on options, tar file is compressed with bzip2
5. The archive is encrypted with a public key of your choice
6. The archive is signed with a public key of your choice (not necessarily the same as in #6)
7. A manifest of all files in the archive + checksums is stored as a JSON file
8. The manifest is signed (using ASCII instead of binary to keep it readable)
9. Parity file(s) are created to allow the archive to be restored should bitrot happen
10. Filelist with checksums is created
11. All extra files (filelist, parity, etc) files are signed
12. Resulting files are uploaded to the cloud (may take a while with AWS Glacier, skipped if no cloud config))
13. Backup is copied to safe keeping (if done directory is specified)
14. Prep directory is emptied
15. New backup is added to local database
16. Local database is saved as JSON

A lot of things here can be customized, but in a nutshell, this is what the tool does with all the bells and whistles enabled.

All filenames generated by the tool are based on date and time (YYYYMMDD-HHMMSS-xxxxx, time is in UTC), which helps you figure out where data might hide if you need to find it and have lost the original local database. Also allows you to restore files in the *correct* order (since the tool may have more than one copy of the same file, see `--modified`).

If you have the local database, you find that each file also points out which archive it belongs to. When a file is modified, it adds a new memberof entry. By sorting the backups field you can easily find the latest backup. Same applies to the an individual file, by sorting the memberof field you can find the latest version (or an old one).

# Disclaimer

I use this backup tool myself to safely keep a backup of my family's private email (I run the server so it seemed prudent). It's also used for all our photos and homevideos, not to mention all scanned documents (see LagerDox, another pet project on github).

**BUT!**<br>
If you loose any content as a result of using this tool (directly or indirectly) you cannot hold me responsible for your loss or damage.

There, I said it. Enough with disclaimers now :-)

## Requirements

In order to be able to run this, you need a few other parts installed.

- OpenPGP / GNU Privacy Guard (typically referred to as `gpg`)
- python-gnupg - Encryption & Signature (NOT `gnupg`, it's `python-gnupg`)
  Ubuntu comes with a version, but unfortunately it's too old. You should install this using the `pip` tool to make sure you get a current version.
- par2 - Parity tool
- aws - In order to upload archive to glacier

### Installing on Ubuntu

This is the simple version which points out what commands to run. Please consider reading through before running since it will install things (such as pip) in a manner which you might not agree with. It is based on what and how I installed the requirements on a Ubuntu LTS 14 release.

1. GPG
  Easy enough, ubuntu comes with it pre-installed
2. GnuPG (requires PIP)
  ```
  sudo apt-get install python-dev
  sudo apt-get install python-pip
  sudo pip install python-gnupg
  ```

3. PAR2 for parity
  ```
  sudo apt-get install par2
  ```

4. AWS Glacier
  ```
  sudo apt install awscli
  ```

For more details, see the [step-by-step guide](https://github.com/mrworf/iceshelf/wiki) in the wiki.

## Configuration file

Iceshelf requires a config file to work. You may name it whatever you want and it may exist wherever you want. The important part is that you point it out to the tool.

Here's what it all does...

### Section [sources]

Contains all the directories you wish to backup. Can also be individual files. You define each source by name=path/file, for example:

```
my home movies=/mnt/storage/homemovies
my little file=/mnt/documents/birthcertificate.pdf
```

*default is... no defined source*

### Section [paths]

Iceshelf needs some space for both temporary files and the local database.

#### prep dir

The folder to hold the temporary files, like the in-transit tar files and related files, so a ram-backed storage (such as tmpfs) is a **VERY BAD IDEA**. Especially since AWS Glacier uploads can take "a while".

*default is `backup/inprogress/`*

#### data dir

Where to store local data needed by iceshelf to function. Today that's a checksum database, tomorrow, who knows? Might be good to back up (yes, you can do that).

*default is `backup/metadata/`*

#### done dir

Where to store the backup once it's been completed. If this is blank, no backup is stored. Also see `max keep` under `[options]` for additional configuration. By setting this option and not defining a glacier config, you can use iceshelf as a standalone backup tool without dependencies on AWS Glacier.

Please note that it copies the data to the new location and only on success will it delete the original archive files.

*default is `backup/done/`*

#### create paths

By default, iceshelf does not create the done, data or preparation directories, it leaves this responsibility to the user. However, by setting this option to yes, it will create the needed structure as described in the configuration file.

*default is `no`*

### Section [options]

There are quite a few options for you to play with. Unless otherwise specified, the options are toggled using `yes` or `no`.

#### check update

Will try to detect if there is a new version of iceshelf available and if so, print out the changes. It's done as the first operation before starting the backup. It requires you run iceshelf from its git repository and that `git` is available. If there is no new version or it's not run from the git repository, then it fails silently.

*default is no, don't check for updates*

#### max size

Defines the maxium size of the *uncompressed* data. It will never go above this, but depending on various other options, the resulting backup files may exceed it.

This option is defined in bytes, but can also be suffixed with K, M, G or T to indicate the unit. We're using true powers of 2 here, so 1K = 1024.

A value of zero or simply blank (or left out) will make it unlimited (unless `add parity` is in-effect)

**If the backup didn't include all files due to exceeded max size, then iceshelf will exit with code 10. By rerunning iceshelf with the same parameters it will continue where it left of. If you do this until it exits with zero, you'll have a full backup.

This behavior is to allow you to segment your uploads into a specific size.**

*default is blank, no limit*

#### change method

How to detect changes. You have a few different modes, the most common is `data`, but also `sha1` (same as data actually), `sha256` and `sha512` works. Iceshelf uses hashes of the data which is then compared to see changes. While sha1 usually is good enough, you can also specify `sha256` or `sha512` if you feel it is warranted.

Note that switching between various methods will not upgrade all checksum on the next run, only files which have changes will get the new checksum to avoid unnecessary changes.

*default is `data`*

#### delta manifest

Save a delta manifest with the archive as separate file. This is essentially a JSON file with the filenames and their checksums. Handy if you ever loose the entire local database since you can download all your manifests in order to locate the missing file.

Please keep in-mind that this is a *delta* manifest, it does not contain anything but the files in this backup, there are no references to any other files from previous backups.

*default is `yes`*

#### compress

Controlling compression, this option can be `yes`, `no`, `force`. While `no` is obvious (never compress), `yes` is somewhat more clever. It will calculate how many of the files included in the backup are considered compressible (see `incompressible` as well) and engage compression if 20% or more is considered compressible.

Now, `force` is probably more obvious, but we cover it anyway for completeness. It essentially overrides the logic of `yes` and compresses regardless of the content.

*default is `yes`*

#### persuasive

While a fun name for an option, it essentially says that even if the next file won't fit within the max size limits, it should continue and see if any other file fits. This is to try and make sure that all archives are of equal size. If no, it will abort the moment a it gets to a file which won't fit the envelope.

*default is `yes`*

#### ignore overlimit

If `yes`, this will make iceshelf return a success code once all files are backed up, even if it has skipped files that are larger than the max size. So if you have 10 files and one is larger than max size, then 9 files will be backed up and it will still return OK (exit code 0), without this option, it would have failed and had a non-zero exit code.

*default is `no`*

#### incompressible

Using this option, you can add additional file extensions which will be considered incompressible by the built-in logic.

*default is blank, relying only on the built-in list*

#### max keep

Defines how many backups to keep in the `done dir` folder. If it's zero or blank, there's no limit. Anything else defines the number of backups to keep. It's based on FIFO, oldest backup gets deleted first. This option is pointless without defining a `done dir`.

*default is zero, unlimited storage*

#### prefix

Optional setting, allows you to add the selected prefix to all files produced by the tool. If not set, then no prefix is added.

*default is no prefix*

#### detect move

This is an *experimental* feature which tries to detect when you've just moved a file or renamed it. It will only log the change to the JSON manifest and will not upload the file, since it's the same file.

It's a very new feature and should be used with caution. It will track what backup the original file was in and what the name was, so it should be able to provide details for restore of moved files, but it's not 100% tested.

*default is `no`*

#### create filelist

Adds an additional file, called `filelist.txt` which is a shasum compatible file which details the hash of each file in the backup (the produced backup files, not the backed up files) as well as their corresponding sha1 which can be checked with shasum, like so `shasum -c filelist.txt`. This is to tell you what files belong to the backup. It's used by iceshelf-restore. File will also be signed if signature is enabled (see security).

*default is `yes`*

### Section [exclude]

This is an optional section, by default iceshelf will backup every file it finds in the source. But sometimes that's not always appreciated. This section allows you to define some exclusion rules.

You define rules the same way you do sources, by name=rule, for example:

```
no zip files=*.zip
no cache=/home/user/cache
...
```

In the simplest form, the rule is simply a definition of what the filename (including path) is starting with. If this matches, it's excluded. All rules are CaSe-InSeNsItIvE.

#### Prefixes

You can however make it more complex by using prefixes. By prefixing the rule with a star (*) the rule will match starting from the end. By prefixing with a questionmark (?) the rule will match any file containing the rule. Finally you can also use less-than or more-than (&lt; or &gt;) followed by a size to exclude by size only.

But wait, there's more. You can on top of these prefixes add an additional prefix (a pre-prefix) in the shape of an exclamationmark. This will *invert* the rule and make it inclusive instead.

Why would you want to do this?

Consider the following:
```
[exclude]
alldocs=!*.doc
no odd dirs=/some/odd/dir/
```

In a structure like this:

```
/some/
/some/data.txt
/some/todo.doc
/some/odd/dir/
/some/odd/dir/moredata.txt
/some/odd/dir/readme.doc
```

It will backup the following:

```
/some/data.txt
/some/todo.doc
/some/odd/dir/readme.doc
```

Notice how it snagged a file from inside an excluded folder? Pretty convenient. However, in order for this to work, you must consider the order of the rules. If you change the order to:

```
[exclude]
no odd dirs=/some/odd/dir/
alldocs=!*.doc
```

The `no odd dirs` would trigger first and the second rule would never get a chance to be evaluated. If you're having issues with the rules, consider running iceshelf with `--changes` and `--debug` to see what it's doing.

Finally, you can also reference external files containing exclusion rules. This makes it easy to use readymade rules for various items you'd like to backup. Including a external rule file is done by prefixing the filename with a pipe ```|``` character. For example, to include "my-rules.excl", you'd write the following:

```
[exclude]
my rules=|/some/path/my-rules.excl
```

What essentially happens is that the "my rules" line is replaced with all the rules defined inside my-rules.excl. The only restriction of the external rules reference is that you are not able to reference other external rule files from an external rule file (yes, no recursion for you).

### Section [glacier]

This is, believe it or not, optional. Yes, you can run iceshelf locally and have it store the backup on whatever storage that the `done dir` option is pointing at. However, should you decide to use this for glacier, you'll first of all need to make sure that aws is installed.

You can of course use both the glacier options and `done dir` if you prefer a local copy of any AWS Glacier copy.

#### vault

The name of the vault. Iceshelf will automatically create the vault if it doesn't exist, it will also avoid doing so to minimize the operations towards the AWS to avoid extra fees. It does this by only creating/checking the existance of the vault when you run iceshelf the first time or when you change the vault name from its previous name.

#### threads

The number of threads to use during upload. The default is 4. This can be tweaked to improve performance. For instance, when sending content to far away datacenters the throughput per connection might be as low as 200K/s, which will make uploads take a long time. By using more threads, iceshelf will upload multiple parts of a file concurrently.

NOTE! You will need to run ```aws configure``` for the user which will be running iceshelf in order to set up the aws tool. Iceshelf will try to make sure that this has been done and stop before starting the process.

### Section [security]

From here you can control everything which relates to security of the content and the parity controls. Make sure you have GPG installed or this will not function properly.

#### encrypt

Specifies the GPG key to use for encryption. Usually an email address. This option can be used independently from sign and can also use a different key.

Only the archive file is encrypted.

*default is blank*

#### encrypt phrase

If your encryption key needs a passphrase, this is the place you put it.

*default is blank*

#### sign

Specifies the GPG key to use for signing files. Usually an email address. This option can be used independently from encrypt and can also use a different key.

Using signature will sign *every* file associated with the archive, including the archive itself. It gives you the benefit of being able to validate the data as well as detecting if the archive has been damaged/tampered with.

See `add parity` for dealing with damaged archive files.

*default is blank*

#### sign phrase

If your signature key needs a passphrase, this is the place you put it.

*default is blank*

#### encrypt manifest

If you're worried that the use of a manifest file (which describes the changes contained in the backup, see `delta manifest` under `options`), specifying this option will encrypt the manifest as well (using the same key as `encrypt` above). If you haven't enabled `delta manifest`, this option has no effect.

*default is `yes`*

#### add parity

Adds a PAR2 parity file, allowing you to recover from errors in the archive, should that have happened. These files will never be encrypted, only signed if you've enabled signature. The value for this option is the percentage of errors in the archive that you wish to be able to deal with.

The value ranges from 0 (off) to 100 (the whole file).

Remember, if you ask for 50%, the resulting archive files *will* be roughly 50% larger.

For security people, this option is acting upon the already encrypted and signed version of the archive, so even at 100%, there won't be any data which can be used to get around the encryption.

There is unfortunately also a caveat with using parity. Due to a limitation of the PAR2 specification, `max size` will automatically be set to 32GB, regardless if you have set it to unlimited or >32GB.

*default is zero, no parity, to avoid the 32GB limit*

## Commandline

You can also provide a few options via the commandline, these are not available in the configuration file.

`--changes` will show you what *would* be backed up, if you were to do it

`--logfile` redirects the log output to a separate file, otherwise warning and errors are shown on the console. Enabling file logging will also enable full debugging.

`--find <string>` will show any file and backup which contains the `<string>`

`--modified` shows files which have changed and the number of times, helpful when you want to find what you need to exclude from your backup (such as index files, cache, etc)

`--show <archive>` lists all files components which makes up a particular backup. This is refering to the archive file, manifest, etc. Not the contents of the actual backup. Helpful when you need to retreive a backup and you want to know all the files.

`--full` forces a complete backup, foregoing the incremential logic.

`--list files` shows the current state of your backup, as iceshelf knows it

`--list members` shows the files that are a part of your backup and where to find the latest copy of that file

`--list sets` shows the backups you need to retrieve to restore a complete backup (please unpack in old->new order)

No matter what options you add, you *must* point out the configuration file, or you will not get any results.

## Return codes

Depending on what happened during the run, iceshelf will return the following exit codes:

0 = All good, operation finished successfully

1 = Configuration issue

2 = Unable to gather all data, meaning that while creating the archive to upload, some kind of I/O related error happened. The log should give you an idea of what. Can happen when files disappear during archive creation

3 = Amount of files to backup exceed the `max size` parameter and `persuasive` wasn't enabled

10 = Backup was successful, but there are more files to backup. Happens if `persuasive` and `max size` is enabled and the amount of data exceeds `max size`. Running the tool again will gather any files which weren't backed up. Ideally you continue to run the tool until it returns 0

255 = Generic error, see log output

# What's missing?

There is as of yet no way to have iceshelf retreive the backup it created and uploaded. For now you're left to use the `aws` tool itself to do that. Once you've retrieved the file(s), you can either extract it manually yourself or try the [iceshelf-restore](README.iceshelf-restore.md) tool which is in beta. It's fairly robust and is able to deal with most circumstances. It will not, however, allow you to easily download files from glacier. It's coming later.

# Thoughts

- Better options than par2 which are open-source?
- JSON is probably not going to cut-it in the future for local metadata storage

# FAQ

## I keep getting "Signature not yet current" errors when uploading

This is caused by your system clock being off by more than 5 minutes. It's highly recommended that you run a time synchronization daemon such as NTPd on the machine which is responsible for uploading the backup to glacier.

## When I run the tool, it says "Current GnuPG python module does not support file encryption, please check FAQ section in documentation"

Unfortunately, there is both a gnupg and a python-gnupg implementation. This tool relies on the latter. If you get this error, then you've installed the `gnupg` version instead of `python-gnupg`.
To fix this, please uninstall the wrong one using either the package manager or `sudo pip uninstall gnupg` followed by the correct one `sudo pip install python-gnupg`

## I get "Filename '&lt;some file&gt;' is corrupt, please rename it. Will be skipped for now" warnings

This happens, in particular on Unix filesystems where you might, at one point, have stored filename information encoded in a non-UTF8 format (such as Latin1, or similar). When you then upgraded to UTF8, these files remained. Usually doing a `ls -la <some file's folder>` it will show up but with a questionmark where the character should be. This is because it's not compatible with UTF8.

To fix it, simply rename the file and it will work as expected.

## What about the local database?

Yes, it's vulnerable to tampering, bitrot and loss. But instead of constructing something to solve that locally, I would recommend you simply add an entry to the [sources] section of the config:

```
iceshelf-db=/where/i/store/the/checksum.json
```

And presto, each copy of the archive will have the previous database included. Which is fine because normally the `delta manifest` option is enabled which means that you got it all covered.

If this turns out to be a major concern/issue, I'll revisit this question.

## How am I supposed to restore a full backup?

Using the `--list sets` option, iceshelf will list the necessary backups you need to restore and in the order to do it. If a file was moved, the tool will display what the original name was and what the new name is supposed to be.

There is also an experimental tool called [iceshelf-restore](README.iceshelf-restore.md) which you can use to more easily extract a backup. It will use your `iceshelf.conf` file and do all the validation as well as potential repair as needed.

## After doing some development on the code, how will I know something didn't break?

Please use the testsuite and run a complete iteration with GPG and PAR2. Also extend the suite if needed to cover any specific testcase which was previously missed.

If you submit a pull request, please include the output from the testsuite.
